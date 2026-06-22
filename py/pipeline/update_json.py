"""
Update web/data/detections.json with new detections.

Rules:
- Duplicate check: new detection within 500m of existing → update confirmed_at + confidence
  (inactive records are excluded from duplicate matching)
- Status management:
    active:      detected or re-detected within last 3 months
    unconfirmed: 3–6 months since last detection
    inactive:    6+ months since last detection (kept in JSON, hidden on map)
- New detections always start as "active"
"""

import json
from datetime import datetime, timezone, timedelta
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path

DETECTIONS_JSON = (
    Path(__file__).parent.parent.parent / "web" / "data" / "detections.json"
)

DUPLICATE_RADIUS_M = 500
ACTIVE_MONTHS = 3
UNCONFIRMED_MONTHS = 6
DATETIME_FMT = "%Y-%m-%d %H:%M"


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in metres between two lat/lon points."""
    R = 6_371_000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlam = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlam / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime(DATETIME_FMT)


def _update_statuses(records: list[dict], now: datetime) -> list[dict]:
    """Recompute status for all records based on confirmed_at age."""
    for r in records:
        confirmed = datetime.strptime(r["confirmed_at"], DATETIME_FMT).replace(
            tzinfo=timezone.utc
        )
        age_months = (now - confirmed).days / 30.44
        if age_months <= ACTIVE_MONTHS:
            r["status"] = "active"
        elif age_months <= UNCONFIRMED_MONTHS:
            r["status"] = "unconfirmed"
        else:
            r["status"] = "inactive"
    return records


def update_detections(
    new_detections: list[dict],
    json_path: Path = DETECTIONS_JSON,
    is_demo: bool = False,
) -> None:
    """
    Merge new_detections into detections.json.

    new_detections: list of dicts with at least:
      lat, lon, confidence, source
    Optional fields: district (added by caller if available)
    """
    now = datetime.now(timezone.utc)

    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
    else:
        data = {"generated_at": "", "is_demo": is_demo, "detections": []}

    existing = data["detections"]

    # Separate active candidates for duplicate matching (exclude inactive)
    matchable = [r for r in existing if r.get("status") != "inactive"]

    for det in new_detections:
        matched = None
        for record in matchable:
            dist = _haversine_m(det["lat"], det["lon"], record["lat"], record["lon"])
            if dist <= DUPLICATE_RADIUS_M:
                matched = record
                break

        if matched:
            matched["confirmed_at"] = _now_str()
            matched["confidence"] = det["confidence"]
            if "source" in det:
                matched["source"] = det["source"]
        else:
            existing.append({
                "lat": det["lat"],
                "lon": det["lon"],
                "confidence": det["confidence"],
                "detected_at": _now_str(),
                "confirmed_at": _now_str(),
                "status": "active",
                "source": det.get("source", "Unknown"),
                "district": det.get("district", ""),
            })

    existing = _update_statuses(existing, now)
    data["detections"] = existing
    data["generated_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    data["is_demo"] = is_demo

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Updated {json_path}: {len(existing)} total records, {len(new_detections)} new/updated.")


if __name__ == "__main__":
    # Quick smoke test with a dummy detection
    sample = [{
        "lat": -3.7491,
        "lon": -73.2538,
        "confidence": 0.91,
        "source": "Ensemble (Sentinel-2 + Planet)",
        "district": "Maynas, Loreto",
    }]
    update_detections(sample, is_demo=True)
