# user-approval-system-759-768

This workspace contains the Social Media Database container resources (SQLite).

- Container root: social_media_database
- See social_media_database/README.md for initialization and usage.

After initializing/creating the DB file, ensure the backend points to it via:
- Backend .env: `SQLITE_DB=/absolute/or/relative/path/to/your.db`
- Default fallback in backend is `./data/social_media.db`

Typical local setup:
1. Initialize the DB under social_media_database (e.g., ./myapp.db)
2. Set backend `SQLITE_DB` to that path
3. Start backend on port 3001 and frontend on port 3000