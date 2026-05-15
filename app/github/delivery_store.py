"""Simple in-memory store for processed GitHub delivery IDs.

This is intentionally minimal and only suitable for development/testing.
In production use a durable store such as Redis/Postgres/DynamoDB.
"""

from typing import Set

_processed: Set[str] = set()


def is_processed(delivery_id: str) -> bool:
    if not delivery_id:
        return False
    return delivery_id in _processed


def mark_processed(delivery_id: str) -> None:
    if not delivery_id:
        return
    _processed.add(delivery_id)


def clear_store() -> None:
    """Clear the in-memory store (useful for tests)."""
    _processed.clear()

