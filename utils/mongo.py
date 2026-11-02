import os

import streamlit as st
from pymongo import ASCENDING, MongoClient


def _setting(name, default=""):
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value or os.getenv(name, default)


MONGODB_URI = _setting("MONGODB_URI", "mongodb://127.0.0.1:27017")
MONGODB_DATABASE = _setting("MONGODB_DATABASE", "hospital_finder")


@st.cache_resource(show_spinner=False)
def get_client():
    if not MONGODB_URI:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGODB_URI in the environment or Streamlit secrets."
        )
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client


def get_database():
    return get_client()[MONGODB_DATABASE]


def users_collection():
    collection = get_database()["users"]
    collection.create_index([( "email", ASCENDING)], unique=True)
    return collection


def interactions_collection():
    return get_database()["interactions"]


def hospitals_collection():
    return get_database()["hospitals"]


def mongo_status():
    try:
        get_client().admin.command("ping")
        return True, f"Connected to MongoDB database '{MONGODB_DATABASE}'."
    except Exception as exc:
        return False, str(exc)