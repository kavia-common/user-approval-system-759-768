# Migrations

- Migrations are Python files in migrations/ with a numeric prefix and an upgrade(conn) function.
- init_db.py discovers and applies pending migrations in order.
- This approach avoids multi-statement SQL files and aligns with the "execute statements one at a time" guidance.

To apply:
  python3 init_db.py
To apply plus seed dev data:
  python3 init_db.py --seed
To reset DB:
  python3 init_db.py --reset
