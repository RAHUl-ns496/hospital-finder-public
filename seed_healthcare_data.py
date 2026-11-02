import json
import os
from datetime import datetime, timezone

from utils.mongo import get_database


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "healthcare_seed.json")


def seed():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    database = get_database()
    seeded_at = datetime.now(timezone.utc)

    for collection_name, records in data.items():
        collection = database[collection_name]
        collection.delete_many({"source": "demo_seed"})
        documents = [
            dict(record, source="demo_seed", seeded_at=seeded_at)
            for record in records
        ]
        if documents:
            collection.insert_many(documents)
        print(f"Seeded {len(documents)} records into {collection_name}.")


if __name__ == "__main__":
    seed()
