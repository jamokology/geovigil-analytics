"""
GeoVigil Analytics — weekly pipeline entry point.

Register this script with Windows Task Scheduler:
  Program: C:\path\to\.venv\Scripts\python.exe
  Arguments: C:\path\to\py\daily_run.py
  Start in: C:\path\to\repo

Environment variables required (set in Task Scheduler or a .env file):
  CDSE_USER, CDSE_PASSWORD   — Copernicus Data Space
  PLANET_API_KEY             — Planet NICFI

Stages:
  1. Fetch Sentinel-2 imagery (last 7 days)
  2. Fetch Planet NICFI mosaic (previous month)
  3. Run YOLO inference on each source
  4. Ensemble via WBF
  5. Update detections.json
  6. Git commit & push → Cloudflare Pages auto-deploy
"""

import sys
import traceback
from pathlib import Path
from datetime import date

# Allow imports from py/
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.fetch_sentinel import fetch_sentinel
from pipeline.fetch_planet import fetch_planet
from pipeline.run_inference import run_inference
from pipeline.ensemble import ensemble_detections
from pipeline.update_json import update_detections
from pipeline.git_push import commit_and_push

DRY_RUN = "--dry-run" in sys.argv  # skip git push when testing


def main() -> None:
    print("=== GeoVigil Analytics pipeline start ===")

    # 1. Fetch imagery
    print("[1/6] Fetching Sentinel-2...")
    sentinel_images = fetch_sentinel()

    print("[2/6] Fetching Planet NICFI...")
    planet_images = fetch_planet()

    # 2. Inference
    print("[3/6] Running Sentinel-2 inference...")
    sentinel_dets = run_inference(sentinel_images, source="Sentinel-2")

    print("      Running Planet inference...")
    planet_dets = run_inference(planet_images, source="Planet NICFI")

    # 3. Ensemble
    print("[4/6] Ensembling detections (WBF)...")
    merged = ensemble_detections(sentinel_dets, planet_dets)
    print(f"      {len(merged)} detections after ensemble.")

    # 4. Update JSON
    print("[5/6] Updating detections.json...")
    update_detections(merged, is_demo=False)

    # 5. Push
    print("[6/6] Committing and pushing...")
    commit_and_push(dry_run=DRY_RUN)

    print("=== Pipeline complete ===")


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as e:
        print(f"\n[STUB] {e}", file=sys.stderr)
        sys.exit(2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
