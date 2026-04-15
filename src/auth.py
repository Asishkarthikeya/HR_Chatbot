"""User authentication backed by ChromaDB.

Stores user credentials in a dedicated Chroma collection. Passwords are salted
and hashed with SHA-256. Lookups use metadata filtering for exact username match
(no semantic search — we store a throwaway document string just to satisfy Chroma).
"""
import hashlib
import logging
import secrets
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions

from src.config import CHROMA_PERSIST_DIR, USERS_COLLECTION_NAME

logger = logging.getLogger(__name__)

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        ef = embedding_functions.DefaultEmbeddingFunction()
        _collection = _client.get_or_create_collection(
            name=USERS_COLLECTION_NAME,
            embedding_function=ef,
        )
    return _collection


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}::{password}".encode()).hexdigest()


def signup(
    username: str,
    password: str,
    full_name: str,
    role: str,
    department: str,
) -> tuple[bool, str]:
    username = username.strip().lower()
    full_name = full_name.strip()
    if not username or not password:
        return False, "Username and password are required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    if not full_name:
        return False, "Full name is required."

    col = _get_collection()
    existing = col.get(where={"username": username})
    if existing["ids"]:
        return False, f"Username '{username}' already exists. Please log in instead."

    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)

    col.add(
        ids=[username],
        documents=[f"ICE employee profile — {full_name}"],
        metadatas=[{
            "username": username,
            "full_name": full_name,
            "role": role,
            "department": department,
            "salt": salt,
            "password_hash": pw_hash,
        }],
    )
    logger.info(f"[Auth] Registered new user: {username} ({role})")
    return True, f"Welcome aboard, {full_name}! Your account has been created."


def login(username: str, password: str) -> tuple[Optional[dict], str]:
    username = username.strip().lower()
    if not username or not password:
        return None, "Username and password are required."

    col = _get_collection()
    result = col.get(where={"username": username})
    if not result["ids"]:
        return None, "No account found with that username. Please sign up first."

    meta = result["metadatas"][0]
    if _hash_password(password, meta["salt"]) != meta["password_hash"]:
        return None, "Incorrect password."

    user = {
        "username": meta["username"],
        "full_name": meta["full_name"],
        "role": meta["role"],
        "department": meta["department"],
    }
    logger.info(f"[Auth] Login successful: {username}")
    return user, f"Welcome back, {meta['full_name']}."


def login_or_create(username: str, password: str) -> tuple[Optional[dict], str]:
    """Log in if the user exists, otherwise auto-register them.

    New users are created with sensible defaults (role=Employee, full_name
    derived from the username). On repeat logins, the stored password is
    validated — so returning users still get rejected on wrong password.
    """
    username = username.strip().lower()
    if not username or not password:
        return None, "Please enter a username and password."
    if len(password) < 4:
        return None, "Password must be at least 4 characters."

    col = _get_collection()
    existing = col.get(where={"username": username})

    if existing["ids"]:
        meta = existing["metadatas"][0]
        if _hash_password(password, meta["salt"]) != meta["password_hash"]:
            return None, "Incorrect password for this username."
        user = {
            "username": meta["username"],
            "full_name": meta["full_name"],
            "role": meta["role"],
            "department": meta["department"],
        }
        logger.info(f"[Auth] Returning user: {username}")
        return user, f"Welcome back, {meta['full_name']}."

    # New user — auto-register
    display_name = " ".join(w.capitalize() for w in username.replace(".", " ").replace("_", " ").split())
    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    col.add(
        ids=[username],
        documents=[f"ICE employee profile — {display_name}"],
        metadatas=[{
            "username": username,
            "full_name": display_name,
            "role": "Employee",
            "department": "",
            "salt": salt,
            "password_hash": pw_hash,
        }],
    )
    user = {
        "username": username,
        "full_name": display_name,
        "role": "Employee",
        "department": "",
    }
    logger.info(f"[Auth] Auto-registered new user: {username}")
    return user, f"Welcome, {display_name}. Your account has been created."


def user_count() -> int:
    return _get_collection().count()
