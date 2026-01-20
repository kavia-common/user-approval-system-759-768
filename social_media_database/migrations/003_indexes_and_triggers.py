# Migration 003: Indexes and triggers for performance and counters

def upgrade(conn):
    cur = conn.cursor()

    # Useful indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reactions_post_id ON reactions(post_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reactions_user_id ON reactions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_followers_following ON followers(following_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_followers_follower ON followers(follower_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_analytics_daily_date ON analytics_daily(date)")

    # Triggers to update post counters
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_reaction_after_insert
        AFTER INSERT ON reactions
        FOR EACH ROW
        BEGIN
            UPDATE posts
            SET
                like_count = like_count + CASE WHEN NEW.type='like' THEN 1 ELSE 0 END,
                comment_count = comment_count + CASE WHEN NEW.type='comment' THEN 1 ELSE 0 END,
                share_count = share_count + CASE WHEN NEW.type='share' THEN 1 ELSE 0 END
            WHERE id = NEW.post_id;
        END;
    """)

    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_reaction_after_delete
        AFTER DELETE ON reactions
        FOR EACH ROW
        BEGIN
            UPDATE posts
            SET
                like_count = like_count - CASE WHEN OLD.type='like' THEN 1 ELSE 0 END,
                comment_count = comment_count - CASE WHEN OLD.type='comment' THEN 1 ELSE 0 END,
                share_count = share_count - CASE WHEN OLD.type='share' THEN 1 ELSE 0 END
            WHERE id = OLD.post_id;
        END;
    """)
