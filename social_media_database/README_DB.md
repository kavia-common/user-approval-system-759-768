# Social Media Database (SQLite)

This folder contains the SQLite database for the Social Media Dashboard.

Contents:
- init_db.py: Initialize DB, apply migrations, and optionally seed dev data.
- migrations/: Ordered Python migration scripts with an upgrade(conn) function.
- seeds/: Optional dev data seeding scripts.
- helpers/: Lightweight Python DB helpers for backend or scripts.
- db_shell.py: Interactive SQLite shell.
- db_visualizer/: Minimal DB viewer (Node/Express). Use sqlite.env to point it to your DB.

Environment
- SQLITE_DB: Optional file path to the SQLite database (defaults to ./myapp.db). The orchestrator for this container provides SQLITE_DB in runtime environments.

Quickstart
1) Initialize or migrate:
   python3 init_db.py
   # or include seeds:
   python3 init_db.py --seed

2) Interactive shell:
   ./db_shell.py
   # Commands: .tables, .schema [table], .describe [table]

3) Visualize data:
   source db_visualizer/sqlite.env
   cd db_visualizer && npm install && npm start
   # Open http://localhost:3000 and choose SQLite

Schema Overview
- users: accounts with username, email, role, status.
- profiles: 1:1 with users, profile metadata.
- posts: user posts with text/media and engagement counters.
- followers: follow relationships (follower_id -> following_id).
- reactions: like/comment/share per post (unique like/share per user/post).
- analytics_daily: per-day rollups (per user and/or per post).
- Views:
  - post_engagement_summary
  - user_stats_summary

Notes
- Foreign keys enabled; cascading deletes clean related data.
- Triggers keep posts.like_count/comment_count/share_count synchronized with reactions.
- Migrations are idempotent; executed once and tracked in schema_migrations.

Seeding
- Seed scripts are idempotent where possible and safe to rerun.
- Use: python3 init_db.py --seed

Helpers
- from helpers.db_helpers import get_connection, get_user_by_username, list_posts_with_engagement, upsert_daily_analytics

Default Connection
- See db_connection.txt created by init_db.py for the absolute path and connection string.

