# ─────────────────────────────────────────────
#  config.py  —  Database credentials
#  ⚠️  NEVER commit this file to Git.
#      It is already listed in .gitignore.
# ─────────────────────────────────────────────

DB_HOST     = "127.0.0.1"    # Use IPv4 explicitly (avoids ::1 IPv6 auth issues)
DB_PORT     = 5432              # default PostgreSQL port
DB_USER     = "postgres"        # your PostgreSQL username (usually 'postgres')
DB_PASSWORD = "2005"          # PostgreSQL password
DB_NAME     = "sentiment_db"   # database will be created automatically
