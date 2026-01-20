# Migration 002: Create analytics helper views

def upgrade(conn):
    cur = conn.cursor()

    # View: post_engagement_summary
    cur.execute("""
        CREATE VIEW IF NOT EXISTS post_engagement_summary AS
        SELECT
            p.id AS post_id,
            p.user_id,
            COUNT(CASE WHEN r.type = 'like' THEN 1 END) AS likes,
            COUNT(CASE WHEN r.type = 'comment' THEN 1 END) AS comments,
            COUNT(CASE WHEN r.type = 'share' THEN 1 END) AS shares,
            p.like_count,
            p.comment_count,
            p.share_count,
            p.created_at
        FROM posts p
        LEFT JOIN reactions r ON r.post_id = p.id
        GROUP BY p.id
    """)

    # View: user_stats_summary
    cur.execute("""
        CREATE VIEW IF NOT EXISTS user_stats_summary AS
        WITH follower_counts AS (
          SELECT u.id AS user_id,
                 COUNT(f1.follower_id) AS followers,
                 COUNT(f2.following_id) AS following
          FROM users u
          LEFT JOIN followers f1 ON f1.following_id = u.id
          LEFT JOIN followers f2 ON f2.follower_id = u.id
          GROUP BY u.id
        ),
        post_counts AS (
          SELECT user_id, COUNT(*) AS posts
          FROM posts
          GROUP BY user_id
        )
        SELECT
          u.id AS user_id,
          u.username,
          COALESCE(fc.followers, 0) AS followers,
          COALESCE(fc.following, 0) AS following,
          COALESCE(pc.posts, 0) AS posts
        FROM users u
        LEFT JOIN follower_counts fc ON fc.user_id = u.id
        LEFT JOIN post_counts pc ON pc.user_id = u.id
    """)
