"""Reading the live TITO cycles published at tito.uffis.org.

TITO runs hourly and publishes each cycle under `outputs/<country>/<cycle>/`,
where <cycle> is the start time as YYYYMMDD.HHMMSS in UTC, with an index.json
listing every file. About a day of cycles is kept there; older ones are archived
as .tar files that cannot be read in place.
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

_latest = {}


def _get(url):
    def fetch():
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()

    return _retry(fetch)


def exists(url):
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=30):
            return True
    except urllib.error.HTTPError:
        return False


def latest_cycle(slug):
    """The newest published cycle, e.g. '20261023.170000'."""
    cached = _latest.get(slug)
    if cached and time.monotonic() - cached[1] < LATEST_TTL_S:
        return cached[0]
    cycle = json.loads(_get(f"{OUTPUTS}/{slug}/latest.json"))["cycle"]
    _latest[slug] = (cycle, time.monotonic())
    return cycle


def available_cycles(slug):
    """Every cycle still published, newest first.

    latest.json names only the newest cycle and the bucket cannot be listed, so
    each hour back from it is probed for its index.json. An hour is sometimes
    skipped, which is why every hour is checked rather than counting back.
    """
    newest = datetime.strptime(latest_cycle(slug), CYCLE_FORMAT)
    candidates = [
        (newest - timedelta(hours=h)).strftime(CYCLE_FORMAT)
        for h in range(LOOKBACK_HOURS)
    ]
    with ThreadPoolExecutor(max_workers=16) as pool:
        found = pool.map(lambda c: exists(f"{OUTPUTS}/{slug}/{c}/index.json"), candidates)
    return [cycle for cycle, ok in zip(candidates, found) if ok]


def resolve_cycle(value, slug):
    """The cycle stamp a `cycle` argument names, or TRAINING.

    Unset, "latest" and an unresolved "${Variable}" all mean the newest cycle.
    """
    if value == TRAINING:
        return TRAINING
    if isinstance(value, str) and CYCLE_RE.match(value):
        return value
    return latest_cycle(slug)


@lru_cache(maxsize=64)
def cycle_files(slug, cycle):
    """Every path a cycle publishes, relative to the cycle. Cached: a published
    cycle never changes."""
    try:
        index = json.loads(_get(f"{OUTPUTS}/{slug}/{cycle}/index.json"))
    except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard as-is
        raise ValueError(
            f"TITO cycle {cycle} is not available for {slug}; cycles are kept "
            f"for about a day ({exc})"
        ) from exc
    return frozenset(f["path"] for f in index["files"])


def file_url(slug, cycle, path):
    return f"{OUTPUTS}/{slug}/{cycle}/{path}"


def cycle_label(cycle):
    return f"{datetime.strptime(cycle, CYCLE_FORMAT):%Y-%m-%d %H:%M} UTC"


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

    # Site and cycle are both in the URL path; keep them in the name.
    path = cache / url.removeprefix(OUTPUTS + "/").replace("/", "__")
    if not path.exists():
        fd, staged = tempfile.mkstemp(dir=cache, prefix=f"{path.name}.", suffix=".part")
        os.close(fd)
        try:
            urllib.request.urlretrieve(url, staged)
            os.replace(staged, path)
        finally:
            Path(staged).unlink(missing_ok=True)
    return path
