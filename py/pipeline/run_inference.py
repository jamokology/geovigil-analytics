"""
Run YOLO inference on input imagery.

Two separate models:
  - model_sentinel.pt  → Sentinel-2 tiles
  - model_planet.pt    → Planet NICFI quads

Each model outputs a list of raw detections:
  [{"lat": float, "lon": float, "confidence": float, "source": str}, ...]

Requirements (fill in before use):
- Receive model_sentinel.pt and model_planet.pt from predecessor
- Confirm input image format (tile size, bands, normalization) from predecessor
"""

from pathlib import Path
from typing import Literal

# TODO: pip install ultralytics
# from ultralytics import YOLO

MODEL_DIR = Path(__file__).parent.parent.parent / "models"
MODEL_SENTINEL = MODEL_DIR / "model_sentinel.pt"
MODEL_PLANET = MODEL_DIR / "model_planet.pt"

# Confidence threshold — adjust after reviewing model performance
CONF_THRESHOLD = 0.5

Source = Literal["Sentinel-2", "Planet NICFI"]


def _model_path(source: Source) -> Path:
    return MODEL_SENTINEL if source == "Sentinel-2" else MODEL_PLANET


def run_inference(image_paths: list[Path], source: Source) -> list[dict]:
    """
    Run YOLO inference on a list of GeoTIFF/image paths.

    Returns list of raw detections with pixel coords converted to lat/lon.
    Each detection: {"lat": float, "lon": float, "confidence": float, "source": str}
    """
    model_path = _model_path(source)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}\n"
            "Obtain model weights from predecessor and place them in models/."
        )

    # TODO: implement inference
    # from ultralytics import YOLO
    # model = YOLO(str(model_path))
    # results = model(image_paths, conf=CONF_THRESHOLD)
    # Convert bounding box centers → lat/lon using image geotransform (rasterio)
    # Return list of detection dicts

    raise NotImplementedError(
        "run_inference() is a stub. Implement after receiving model weights."
    )


if __name__ == "__main__":
    import sys
    paths = [Path(p) for p in sys.argv[1:]]
    detections = run_inference(paths, source="Sentinel-2")
    for d in detections:
        print(d)
