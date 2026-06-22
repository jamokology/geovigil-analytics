"""
Ensemble detections from Sentinel-2 and Planet models using Weighted Boxes Fusion (WBF).

Dependencies: ensemble-boxes
  pip install ensemble-boxes

WBF paper: https://arxiv.org/abs/1910.13302
"""

from typing import Optional

# pip install ensemble-boxes
# from ensemble_boxes import weighted_boxes_fusion

# IOU threshold for merging overlapping boxes from different models
IOU_THR = 0.5
SKIP_BOX_THR = 0.0001

# Model weights: adjust based on observed precision per source
MODEL_WEIGHTS = [1.0, 1.0]  # [sentinel_weight, planet_weight]


def _latlon_to_norm(lat: float, lon: float) -> tuple[float, float]:
    """Normalize lat/lon to [0, 1] for WBF (using Peru bounding box)."""
    lat_min, lat_max = -18.4, 0.0
    lon_min, lon_max = -81.3, -68.7
    x = (lon - lon_min) / (lon_max - lon_min)
    y = (lat - lat_min) / (lat_max - lat_min)
    return x, y


def _norm_to_latlon(x: float, y: float) -> tuple[float, float]:
    lat_min, lat_max = -18.4, 0.0
    lon_min, lon_max = -81.3, -68.7
    lat = y * (lat_max - lat_min) + lat_min
    lon = x * (lon_max - lon_min) + lon_min
    return lat, lon


def ensemble_detections(
    sentinel_detections: list[dict],
    planet_detections: list[dict],
    iou_thr: float = IOU_THR,
    box_size_deg: float = 0.005,  # ~500m box half-width in degrees
) -> list[dict]:
    """
    Merge Sentinel-2 and Planet detections via WBF.

    Each input detection: {"lat": float, "lon": float, "confidence": float, "source": str}
    Returns merged detections with source set to "Ensemble (Sentinel-2 + Planet)".
    """
    # WBF expects boxes as [x1, y1, x2, y2] normalized to [0, 1]
    def to_boxes(detections: list[dict]) -> tuple[list, list, list]:
        boxes, scores, labels = [], [], []
        for d in detections:
            x, y = _latlon_to_norm(d["lat"], d["lon"])
            boxes.append([
                max(0.0, x - box_size_deg),
                max(0.0, y - box_size_deg),
                min(1.0, x + box_size_deg),
                min(1.0, y + box_size_deg),
            ])
            scores.append(d["confidence"])
            labels.append(0)  # single class: airstrip
        return boxes, scores, labels

    sent_boxes, sent_scores, sent_labels = to_boxes(sentinel_detections)
    plan_boxes, plan_scores, plan_labels = to_boxes(planet_detections)

    boxes_list = [sent_boxes, plan_boxes]
    scores_list = [sent_scores, plan_scores]
    labels_list = [sent_labels, plan_labels]

    # TODO: uncomment after installing ensemble-boxes
    # from ensemble_boxes import weighted_boxes_fusion
    # fused_boxes, fused_scores, _ = weighted_boxes_fusion(
    #     boxes_list, scores_list, labels_list,
    #     weights=MODEL_WEIGHTS,
    #     iou_thr=iou_thr,
    #     skip_box_thr=SKIP_BOX_THR,
    # )

    raise NotImplementedError(
        "ensemble_detections() is a stub. Install ensemble-boxes and uncomment WBF call."
    )

    merged = []
    for box, score in zip(fused_boxes, fused_scores):  # noqa: F821
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        lat, lon = _norm_to_latlon(cx, cy)
        merged.append({
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "confidence": round(float(score), 4),
            "source": "Ensemble (Sentinel-2 + Planet)",
        })
    return merged
