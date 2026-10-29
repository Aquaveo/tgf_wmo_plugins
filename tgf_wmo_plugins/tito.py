"""Reading the live TITO cycles published at tito.uffis.org.

TITO runs hourly and publishes each cycle under `outputs/<country>/<cycle>/`,
where <cycle> is the start time as YYYYMMDD.HHMMSS in UTC, with an index.json
listing every file. About a day of cycles is kept there; older ones are archived
as .tar files that cannot be read in place.

A country may also have a sample cycle under `sample/<country>/`, laid out the
same way: a past event kept for demonstrating the plugins when nothing is
happening live. A sample is named `sample:<stamp>` wherever a cycle is, so it
flows through every plugin like a live cycle; `stamp()` gives the bare stamp
its file names use.
"""

import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path

from tgf_wmo_plugins.common import _retry

OUTPUTS = "https://tito.uffis.org/outputs"
SAMPLES = "https://tito.uffis.org/sample"
CYCLE_FORMAT = "%Y%m%d.%H%M%S"
CYCLE_RE = re.compile(r"^\d{8}\.\d{6}$")
# The bucket deletes a cycle about a day after it is written; probe a little
# further back than that.
LOOKBACK_HOURS = 54
# How long "latest" is trusted before latest.json is read again.
LATEST_TTL_S = 300
# Live downloads older than this are pruned; no cycle lives longer.
CACHE_MAX_AGE_S = 3 * 24 * 3600

LATEST = "latest"
TRAINING = "training"
SAMPLE = "sample"
SAMPLE_PREFIX = "sample:"

_latest = {}


def _get(url):
    def fetch():
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()

    return _retry(fetch)


def exists(url):
    # A one-byte GET, not HEAD: the server keeps answering HEAD with 200 for a
    # cycle it has already expired and refuses to serve.
    request = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(request, timeout=30):
            return True
    except urllib.error.HTTPError:
        return False


def is_sample(cycle):
    return isinstance(cycle, str) and cycle.startswith(SAMPLE_PREFIX)


def stamp(cycle):
    """The YYYYMMDD.HHMMSS stamp a cycle's file names carry."""
    return cycle[len(SAMPLE_PREFIX):] if is_sample(cycle) else cycle


def _root(cycle):
    return SAMPLES if is_sample(cycle) else OUTPUTS


def cycle_time(cycle):
    return datetime.strptime(stamp(cycle), CYCLE_FORMAT)


@lru_cache(maxsize=8)
def sample_cycle(slug):
    """The country's sample cycle, as `sample:<stamp>`."""
    try:
        cycle = json.loads(_get(f"{SAMPLES}/{slug}/latest.json"))["cycle"]
    except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard as-is
        raise ValueError(f"no sample cycle is published for {slug} ({exc})") from exc
    return SAMPLE_PREFIX + cycle


def latest_cycle(slug):
    """The newest published cycle, e.g. '20261023.170000'."""
    cached = _latest.get(slug)
    if cached and time.monotonic() - cached[1] < LATEST_TTL_S:
        return cached[0]
    cycle = json.loads(_get(f"{OUTPUTS}/{slug}/latest.json"))["cycle"]
    _latest[slug] = (cycle, time.monotonic())
    return cycle


def available_cycles(slug, sample=False):
    """Every cycle still published, newest first; with `sample`, the sample's.

    latest.json names only the newest cycle and the bucket cannot be listed, so
    each hour back from it is probed for its index.json. An hour is sometimes
    skipped, which is why every hour is checked rather than counting back.
    """
    newest = sample_cycle(slug) if sample else latest_cycle(slug)
    prefix = SAMPLE_PREFIX if sample else ""
    candidates = [
        prefix + (cycle_time(newest) - timedelta(hours=h)).strftime(CYCLE_FORMAT)
        for h in range(LOOKBACK_HOURS)
    ]
    with ThreadPoolExecutor(max_workers=16) as pool:
        found = pool.map(
            lambda c: exists(f"{_root(c)}/{slug}/{stamp(c)}/index.json"), candidates
        )
    return [cycle for cycle, ok in zip(candidates, found) if ok]


def resolve_cycle(value, slug):
    """The cycle a `cycle` argument names: a stamp, `sample:<stamp>` or TRAINING.

    Unset, "latest" and an unresolved "${Variable}" all mean the newest cycle.
    """
    if value == TRAINING:
        return TRAINING
    if value == SAMPLE:
        return sample_cycle(slug)
    if isinstance(value, str) and CYCLE_RE.match(stamp(value)):
        return value
    return latest_cycle(slug)


@lru_cache(maxsize=64)
def cycle_files(slug, cycle):
    """Every path a cycle publishes, relative to the cycle. Cached: a published
    cycle never changes."""
    try:
        index = json.loads(_get(f"{_root(cycle)}/{slug}/{stamp(cycle)}/index.json"))
    except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard as-is
        raise ValueError(
            f"TITO cycle {cycle} is not available for {slug}; cycles are kept "
            f"for about a day ({exc})"
        ) from exc
    return frozenset(f["path"] for f in index["files"])


def file_url(slug, cycle, path):
    return f"{_root(cycle)}/{slug}/{stamp(cycle)}/{path}"




def cycle_label(cycle, sample_tag="SAMPLE"):
    """`2026-10-16 19:00 UTC`, marked when it is a sample rather than live."""
    label = f"{cycle_time(cycle):%Y-%m-%d %H:%M} UTC"
    return f"{label}, {sample_tag}" if is_sample(cycle) else label


def live_download(url):
    """Fetch a live file once into its own cache dir, pruning expired cycles.

    Every cycle's files carry the cycle stamp in their name, so the cache would
    otherwise grow by a few megabytes an hour for as long as the server runs.
    """
    cache = Path(tempfile.gettempdir()) / "tgf_wmo_live"
    cache.mkdir(exist_ok=True)
    now = time.time()
    for old in cache.iterdir():
        try:
            if now - old.stat().st_mtime > CACHE_MAX_AGE_S:
                old.unlink()
        except FileNotFoundError:
            pass

    # Source, site and cycle are all in the URL path; keep them in the name.
    path = cache / url.removeprefix("https://tito.uffis.org/").replace("/", "__")
    if not path.exists():
        fd, staged = tempfile.mkstemp(dir=cache, prefix=f"{path.name}.", suffix=".part")
        os.close(fd)
        try:
            urllib.request.urlretrieve(url, staged)
            os.replace(staged, path)
        finally:
            Path(staged).unlink(missing_ok=True)
    return path
