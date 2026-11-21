"""Download the UCI Online Retail dataset (public mirror) to data/online_retail.csv."""

from __future__ import annotations

import urllib.request

from cleaning import DATA_URL, RAW_PATH

if RAW_PATH.exists():
    print(f"Already downloaded: {RAW_PATH}")
else:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {DATA_URL} ...")
    urllib.request.urlretrieve(DATA_URL, RAW_PATH)
    print(f"Saved {RAW_PATH} ({RAW_PATH.stat().st_size / 1e6:.0f} MB)")
