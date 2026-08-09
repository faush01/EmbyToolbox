import csv
import gzip
import json
import os
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

import requests

from store_details import load_emby_items, sqlite_create_store_table


DATASET_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"
DATASET_PATH = Path(__file__).with_name("logs") / "imdb-datasets" / "title.ratings.tsv.gz"
DATASET_HEADERS = {
    "Accept": "application/gzip, application/octet-stream, */*",
    "User-Agent": "imdb-ratings/1.0 (non-commercial IMDb dataset client)",
}
EMBY_ITEMS_PATH = "emby_items.tsv"
SQLITE_STORE_PATH = "imdb_ratings.db"


def _metadata_path(dataset_path):
    return dataset_path.with_suffix(dataset_path.suffix + ".metadata.json")


def _load_metadata(dataset_path):
    metadata_path = _metadata_path(dataset_path)
    if not metadata_path.exists():
        return {}
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _response_metadata(response):
    return {
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
        "content_length": response.headers.get("Content-Length"),
        "run_date": response.headers.get("x-amz-meta-run-date"),
    }


def _save_metadata(dataset_path, metadata):
    metadata_path = _metadata_path(dataset_path)
    temporary_path = metadata_path.with_suffix(metadata_path.suffix + ".tmp")
    try:
        temporary_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        os.replace(temporary_path, metadata_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def download_dataset(dataset_path=DATASET_PATH):
    dataset_path = Path(dataset_path)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = dataset_path.with_suffix(dataset_path.suffix + ".tmp")

    if dataset_path.exists():
        with requests.head(DATASET_URL, headers=DATASET_HEADERS, timeout=30) as response:
            response.raise_for_status()
            remote_metadata = _response_metadata(response)
        local_metadata = _load_metadata(dataset_path)
        if remote_metadata["etag"] and remote_metadata["etag"] == local_metadata.get("etag"):
            return False

    try:
        with requests.get(
            DATASET_URL,
            headers=DATASET_HEADERS,
            stream=True,
            timeout=120,
        ) as response:
            response.raise_for_status()
            with temporary_path.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output.write(chunk)
            downloaded_metadata = _response_metadata(response)
        os.replace(temporary_path, dataset_path)
        _save_metadata(dataset_path, downloaded_metadata)
        return True
    finally:
        temporary_path.unlink(missing_ok=True)


def load_target_items(emby_items_path=EMBY_ITEMS_PATH):
    target_items = {}
    for item in load_emby_items(emby_items_path):
        imdb_id = item["imdb_id"].strip().lower()
        if imdb_id:
            target_items[imdb_id] = item
    return target_items


def import_matching_ratings(
    target_items,
    dataset_path=DATASET_PATH,
    sqlite_store=SQLITE_STORE_PATH,
):
    sqlite_create_store_table(sqlite_store)
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    matched_ids = set()

    with closing(sqlite3.connect(sqlite_store)) as connection:
        with gzip.open(dataset_path, "rt", encoding="utf-8", newline="") as input_file:
            rows = csv.DictReader(input_file, delimiter="\t")
            records = []

            for row in rows:
                imdb_id = row["tconst"]
                item = target_items.get(imdb_id)
                if item is None:
                    continue

                rating_details = {
                    "imdb_id": imdb_id,
                    "title": item["name"],
                    "url": f"https://www.imdb.com/title/{imdb_id}/ratings/",
                    "rating": row["averageRating"],
                    "rating_count": row["numVotes"],
                    "user_ratings": [],
                    "updated": updated,
                }
                records.append((imdb_id, json.dumps(rating_details)))
                matched_ids.add(imdb_id)

        connection.execute("DELETE FROM imdb_ratings")
        connection.executemany(
            "REPLACE INTO imdb_ratings (imdb_id, rating) VALUES (?, ?)",
            records,
        )
        connection.commit()

    return len(records), set(target_items) - matched_ids


def main():
    start = time.perf_counter()
    target_items = load_target_items()
    print(f"Loaded IMDb IDs: {len(target_items)}")

    print(f"Checking IMDb ratings dataset at {DATASET_PATH}")
    downloaded = download_dataset()
    print("Downloaded current dataset" if downloaded else "Using cached dataset")
    download_finished = time.perf_counter()

    imported_count, missing_ids = import_matching_ratings(target_items)
    import_finished = time.perf_counter()

    print(f"Imported ratings: {imported_count}")
    print(f"IMDb IDs without ratings: {len(missing_ids)}")
    print(
        "Download {0:.3f}s Import {1:.3f}s Total {2:.3f}s".format(
            download_finished - start,
            import_finished - download_finished,
            import_finished - start,
        )
    )


if __name__ == "__main__":
    main()
