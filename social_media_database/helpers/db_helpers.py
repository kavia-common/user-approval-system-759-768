"""
Lightweight DB query helpers intended to be imported by backend jobs or scripts.

Usage:
    from helpers.db_helpers import get_connection, get_user_by_username, list_posts_with_engagement

All helpers are safe for SQLite and return row tuples or dict-like via row_factory.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple


def _db_path() -> str:
    """Resolve DB path from env SQLITE_DB or default to ./myapp.db"""
    return os.path.abspath(os.getenv("SQLITE_DB", "myapp.db"))


# PUBLIC_INTERFACE
def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory and foreign keys."""
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# PUBLIC_INTERFACE
def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    """Fetch a user row by username."""
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cur.fetchone()


# PUBLIC_INTERFACE
def list_user_followers(user_id: int) -> List[sqlite3.Row]:
    """List followers of a user (who follow the given user_id)."""
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT u.* FROM followers f
            JOIN users u ON u.id = f.follower_id
            WHERE f.following_id = ?
            ORDER BY u.username
            """,
            (user_id,),
        )
        return cur.fetchall()


# PUBLIC_INTERFACE
def list_posts_with_engagement(user_id: Optional[int] = None, limit: int = 50) -> List[sqlite3.Row]:
    """List posts and engagement summary; filter by user if provided."""
    with get_connection() as conn:
        if user_id is None:
            cur = conn.execute(
                """
                SELECT p.*, pes.likes, pes.comments, pes.shares
                FROM post_engagement_summary pes
                JOIN posts p ON p.id = pes.post_id
                ORDER BY p.created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
        else:
            cur = conn.execute(
                """
                SELECT p.*, pes.likes, pes.comments, pes.shares
                FROM post_engagement_summary pes
                JOIN posts p ON p.id = pes.post_id
                WHERE p.user_id = ?
                ORDER BY p.created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
        return cur.fetchall()


# PUBLIC_INTERFACE
def upsert_daily_analytics(user_id: Optional[int], post_id: Optional[int], date: str, **metrics: int) -> None:
    """Upsert analytics_daily metrics for a (user_id, post_id, date)."""
    cols = ["views", "likes", "comments", "shares", "followers_gained", "followers_lost"]
    values = {k: int(metrics.get(k, 0)) for k in cols}

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO analytics_daily (user_id, post_id, date, views, likes, comments, shares, followers_gained, followers_lost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, post_id, date) DO UPDATE SET
                views = views + excluded.views,
                likes = likes + excluded.likes,
                comments = comments + excluded.comments,
                shares = shares + excluded.shares,
                followers_gained = followers_gained + excluded.followers_gained,
                followers_lost = followers_lost + excluded.followers_lost
            """,
            (
                user_id,
                post_id,
                date,
                values["views"],
                values["likes"],
                values["comments"],
                values["shares"],
                values["followers_gained"],
                values["followers_lost"],
            ),
        )
        conn.commit()
