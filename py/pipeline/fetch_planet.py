"""
Fetch Planet Basemaps NICFI monthly cloud-free mosaics (free access tier).

Requirements (fill in before use):
- Planet NICFI access application: https://www.planet.com/nicfi/
- Set PLANET_API_KEY in environment or .env file

Dependencies: planet  (Planet SDK v2)
"""

import os
from pathlib import Path
from datetime import date
from typing import Optional

# TODO: pip install planet
# See: https://planet-sdk-for-python.readthedocs.io/

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "planet"

# NICFI basemap name format: "planet_medres_normalized_analytic_YYYY-MM_mosaic"
NICFI_MOSAIC_PREFIX = "planet_medres_normalized_analytic"

AOI_PERU = {
    "type": "Polygon",
    "coordinates": [[
        [-81.3, 0.0],
        [-68.7, 0.0],
        [-68.7, -18.4],
        [-81.3, -18.4],
        [-81.3, 0.0],
    ]],
}


def fetch_planet(
    year: Optional[int] = None,
    month: Optional[int] = None,
    output_dir: Path = OUTPUT_DIR,
) -> list[Path]:
    """
    Download the NICFI monthly mosaic for the given year/month (defaults to last month).

    Returns list of downloaded GeoTIFF paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    today = date.today()
    if year is None or month is None:
        # Default: previous month (NICFI mosaics lag ~1 month)
        first_of_month = today.replace(day=1)
        prev_month = first_of_month - __import__("datetime").timedelta(days=1)
        year = prev_month.year
        month = prev_month.month

    api_key = os.environ.get("PLANET_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "PLANET_API_KEY must be set as an environment variable."
        )

    mosaic_name = f"{NICFI_MOSAIC_PREFIX}_{year:04d}-{month:02d}_mosaic"

    # TODO: implement download using Planet SDK v2
    # Example:
    #   import planet
    #   async with planet.Session(auth=planet.Auth.from_key(api_key)) as sess:
    #       client = sess.client("basemaps")
    #       mosaic = await client.get_mosaic(mosaic_name)
    #       quads = client.search_quads(mosaic, geometry=AOI_PERU)
    #       async for quad in quads:
    #           await client.download_quad(quad, output_dir)

    raise NotImplementedError(
        f"fetch_planet() is a stub. Implement after obtaining Planet NICFI API key. "
        f"Target mosaic: {mosaic_name}"
    )


if __name__ == "__main__":
    paths = fetch_planet()
    for p in paths:
        print(p)
