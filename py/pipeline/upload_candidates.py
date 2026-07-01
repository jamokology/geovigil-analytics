"""Upload a batch of review candidates from the workstation to Cloudflare.

Uploads each candidate image to the R2 bucket `geovigil-review-images` and
registers its metadata in the D1 database `geovigil-review`, so the
candidates immediately become available in the swipe-review site
(review/public/index.html).

Requires `wrangler` (npm install -g wrangler) authenticated with an API
token that has R2 and D1 edit permission for this Cloudflare account.

Usage:
    uv run python py/pipeline/upload_candidates.py --manifest candidates.csv --batch step2-2025-06-08

manifest CSV columns (header row required):
    image_path,source,lat,lon
        image_path : local path to the candidate tile image
        source     : sentinel_candidate | existing_model | sentinel_triggered_nicfi
        lat,lon    : WGS84 coordinates (optional, may be blank)

Candidate IDs are derived from --batch and the row's 1-based position, e.g.
"step2-2025-06-08-000001". Re-running with the same manifest/batch is safe
to retry (R2 upload + D1 insert use the same deterministic id/key), but will
fail on the D1 insert if that batch was already loaded (candidates.id is a
primary key) — pass a new --batch value for a fresh set of candidates.
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path

D1_DATABASE = "geovigil-review"
R2_BUCKET = "geovigil-review-images"


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(1)


def sql_str(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="CSV file: image_path,source,lat,lon")
    parser.add_argument("--batch", required=True, help="Batch label, e.g. step2-2025-06-08")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    rows = list(csv.DictReader(manifest_path.open()))
    if not rows:
        print("Manifest is empty.", file=sys.stderr)
        raise SystemExit(1)

    inserts = []
    for i, row in enumerate(rows, start=1):
        image_path = Path(row["image_path"])
        if not image_path.exists():
            print(f"Skipping missing file: {image_path}", file=sys.stderr)
            continue

        candidate_id = f"{args.batch}-{i:06d}"
        object_key = f"{args.batch}/{image_path.name}"

        print(f"[{i}/{len(rows)}] uploading {image_path} -> r2://{R2_BUCKET}/{object_key}")
        run([
            "wrangler", "r2", "object", "put",
            f"{R2_BUCKET}/{object_key}",
            "--file", str(image_path),
            "--remote",
        ])

        lat = row.get("lat") or "NULL"
        lon = row.get("lon") or "NULL"
        inserts.append(
            "INSERT INTO candidates (id, image_key, source, batch, lat, lon) VALUES "
            f"({sql_str(candidate_id)}, {sql_str(object_key)}, {sql_str(row['source'])}, "
            f"{sql_str(args.batch)}, {lat}, {lon});"
        )

    if not inserts:
        print("No candidates uploaded.", file=sys.stderr)
        raise SystemExit(1)

    sql_file = manifest_path.with_suffix(".insert.sql")
    sql_file.write_text("\n".join(inserts))
    print(f"Registering {len(inserts)} candidates in D1 ({D1_DATABASE})...")
    run(["wrangler", "d1", "execute", D1_DATABASE, "--remote", "--file", str(sql_file)])

    print(f"Done. {len(inserts)} candidates from batch '{args.batch}' are now live for review.")


if __name__ == "__main__":
    main()
