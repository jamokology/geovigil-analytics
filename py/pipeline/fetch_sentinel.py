"""
Fetch Sentinel-2 imagery from Copernicus Data Space Ecosystem (CDSE).

Requirements (fill in before use):
- CDSE account: https://dataspace.copernicus.eu/
- Set CDSE_USER and CDSE_PASSWORD in environment or .env file

Dependencies: sentinelhub or requests + openeo
"""

import os
from pathlib import Path
from datetime import date, timedelta
from typing import Optional

# TODO: install sentinelhub or openeo once API credentials are available
# pip install sentinelhub  or  pip install openeo

CLOUD_COVER_MAX = 20  # percent
AOI_PERU = {
    # Rough bounding box for Peru — tighten to region of interest
    "west": -81.3,
    "south": -18.4,
    "east": -68.7,
    "north": 0.0,
}
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "sentinel"


def fetch_sentinel(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    output_dir: Path = OUTPUT_DIR,
) -> list[Path]:
    """
    Download Sentinel-2 L2A tiles covering Peru for the given date range.

    Returns list of downloaded file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=7)

    user = os.environ.get("CDSE_USER")
    password = os.environ.get("CDSE_PASSWORD")
    if not user or not password:
        raise EnvironmentError(
            "CDSE_USER and CDSE_PASSWORD must be set as environment variables."
        )

    # TODO: implement download using sentinelhub SentinelHubRequest or openeo
    # Example sentinelhub usage:
    #   from sentinelhub import SHConfig, BBox, CRS, DataCollection, SentinelHubRequest, MimeType, bbox_to_dimensions
    #   config = SHConfig(); config.sh_client_id = user; config.sh_client_secret = password
    #   ...

    raise NotImplementedError(
        "fetch_sentinel() is a stub. Implement after obtaining CDSE credentials."
    )


if __name__ == "__main__":
    paths = fetch_sentinel()
    for p in paths:
        print(p)
