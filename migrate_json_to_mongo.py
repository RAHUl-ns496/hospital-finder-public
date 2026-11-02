import json
import os

from utils.mongo import interactions_collection, users_collection


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(filename, default):
    path = os.path.join(BASE_DIR, "data", filename)
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def migrate():
    users = load_json("users.json", {})
    user_documents = [dict(data, email=email) for email, data in users.items()]
    if user_documents:
        users_collection().delete_many({})
        users_collection().insert_many(user_documents)

    interactions = load_json("interactions.json", {
        "assignments": {}, "messages": [], "pharmacy_orders": {},
        "appointments": [], "medicine_orders": [],
    })
    interactions["_id"] = "app_state"
    interactions_collection().replace_one({"_id": "app_state"}, interactions, upsert=True)
    print(f"Migrated {len(user_documents)} users and interaction data to MongoDB.")


if __name__ == "__main__":
    migrate()
