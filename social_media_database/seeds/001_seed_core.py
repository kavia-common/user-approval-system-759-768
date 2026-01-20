# Seed 001: basic users, profiles, posts, followers, reactions

def run(conn):
    cur = conn.cursor()

    # Users
    users = [
        ("alice", "alice@example.com", "user", 1),
        ("bob", "bob@example.com", "user", 1),
        ("charlie", "charlie@example.com", "admin", 1),
    ]
    for username, email, role, is_active in users:
        cur.execute("""
            INSERT OR IGNORE INTO users (username, email, role, is_active)
            VALUES (?, ?, ?, ?)
        """, (username, email, role, is_active))

    # Profiles
    cur.execute("SELECT id, username FROM users")
    id_map = {u: i for (i, u) in [(row[0], None) for row in []]}  # placeholder to satisfy linter
    # Build username->id map
    cur.execute("SELECT id, username FROM users")
    rows = cur.fetchall()
    uname_to_id = {row[1]: row[0] for row in rows}

    profiles = [
        (uname_to_id["alice"], "Alice A.", "Coffee, code, and cats.", "NYC", None, None, None),
        (uname_to_id["bob"], "Bobby B.", "Traveler and photographer.", "SF", None, None, None),
        (uname_to_id["charlie"], "Charlie C.", "Platform admin", "LA", None, None, None),
    ]
    for p in profiles:
        cur.execute("""
            INSERT OR IGNORE INTO profiles (user_id, full_name, bio, location, avatar_url, website_url, date_of_birth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, p)

    # Posts
    posts = [
        (uname_to_id["alice"], "Hello world! This is my first post.", None, "public"),
        (uname_to_id["alice"], "A private thought.", None, "private"),
        (uname_to_id["bob"], "Loving the weather today!", None, "public"),
    ]
    for user_id, content, media_url, visibility in posts:
        cur.execute("""
            INSERT INTO posts (user_id, content, media_url, visibility)
            VALUES (?, ?, ?, ?)
        """, (user_id, content, media_url, visibility))

    # Followers relationships
    # bob follows alice, charlie follows alice, alice follows bob
    follows = [
        (uname_to_id["bob"], uname_to_id["alice"]),
        (uname_to_id["charlie"], uname_to_id["alice"]),
        (uname_to_id["alice"], uname_to_id["bob"]),
    ]
    for follower_id, following_id in follows:
        cur.execute("""
            INSERT OR IGNORE INTO followers (follower_id, following_id)
            VALUES (?, ?)
        """, (follower_id, following_id))

    # Reactions
    # Fetch post ids
    cur.execute("SELECT id, user_id FROM posts ORDER BY id")
    post_rows = cur.fetchall()
    if post_rows:
        post1 = post_rows[0][0]
        post2 = post_rows[1][0] if len(post_rows) > 1 else None
        post3 = post_rows[2][0] if len(post_rows) > 2 else None

        # likes/comments/shares
        if post1:
            cur.execute("INSERT OR IGNORE INTO reactions (post_id, user_id, type) VALUES (?, ?, 'like')", (post1, uname_to_id["bob"]))
            cur.execute("INSERT OR IGNORE INTO reactions (post_id, user_id, type, comment_text) VALUES (?, ?, 'comment', ?)", (post1, uname_to_id["charlie"], "Great first post!"))
        if post3:
            cur.execute("INSERT OR IGNORE INTO reactions (post_id, user_id, type) VALUES (?, ?, 'like')", (post3, uname_to_id["alice"]))
            cur.execute("INSERT OR IGNORE INTO reactions (post_id, user_id, type) VALUES (?, ?, 'share')", (post3, uname_to_id["charlie"]))

    # Analytics sample daily
    cur.execute("SELECT date('now')")
    today = cur.fetchone()[0]
    for u in uname_to_id.values():
        cur.execute("""
            INSERT OR IGNORE INTO analytics_daily (user_id, post_id, date, views, likes, comments, shares, followers_gained, followers_lost)
            VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?)
        """, (u, today, 10, 2, 1, 1, 1, 0))
