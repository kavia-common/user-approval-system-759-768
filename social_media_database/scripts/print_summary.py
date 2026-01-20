#!/usr/bin/env python3
"""Print a quick summary of users and posts using helpers."""
from helpers.db_helpers import get_connection

def main():
    with get_connection() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM posts")
        posts = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM reactions")
        reactions = cur.fetchone()[0]
        print(f"Users: {users}, Posts: {posts}, Reactions: {reactions}")
        print("\nTop posts:")
        for row in conn.execute("""
            SELECT p.id, u.username, p.content, pes.likes, pes.comments, pes.shares
            FROM post_engagement_summary pes
            JOIN posts p ON p.id = pes.post_id
            JOIN users u ON u.id = p.user_id
            ORDER BY (pes.likes + pes.comments + pes.shares) DESC
            LIMIT 5
        """):
            print(f"- Post #{row['id']} by {row['username']} | L:{row['likes']} C:{row['comments']} S:{row['shares']} | {row['content'][:60]}")

if __name__ == "__main__":
    main()
