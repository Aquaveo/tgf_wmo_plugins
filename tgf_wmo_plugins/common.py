"""Remote I/O shared by the plugins: Zarr stores and downloaded geopackages."""

import os
import tempfile
import time
import urllib.request
from functools import lru_cache
from pathlib import Path


def _retry(fn, attempts=3, base_delay=0.25):
    """Call `fn`, retrying transient failures of a live HTTPS read."""
    for attempt in range(attempts):
        try:
            return fn()
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(base_delay * (attempt + 1))


@lru_cache(maxsize=64)
def open_zarr_store(store_url):
    """Open the public Zarr group at `store_url` read-only.

    fsspec rather than s3fs, since the stores are public and need no AWS stack.
    zarr is imported here because only the storm family needs it.
    """
    import zarr
    from zarr.storage import FsspecStore

    try:
        return _retry(
            lambda: zarr.open_group(FsspecStore.from_url(store_url), mode="r")
        )
    except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard as-is
        raise ValueError(f"could not open zarr store {store_url}: {exc}") from exc


def cached_download(url):
    """Fetch `url` into the temp dir once and return the local path.

    The transfer lands on a staging name and is moved into place only when
    complete, so plugins reading concurrently never open a half-written file.
    """
    path = Path(tempfile.gettempdir()) / url.rsplit("/", 1)[-1]
    if not path.exists():
        fd, staged = tempfile.mkstemp(
            dir=path.parent, prefix=f"{path.name}.", suffix=".part"
        )
        os.close(fd)
        try:
            urllib.request.urlretrieve(url, staged)
            os.replace(staged, path)
        finally:
            Path(staged).unlink(missing_ok=True)
    return path
