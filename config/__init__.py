"""Project configuration package."""
import os

# Only activate PyMySQL when a MySQL database is actually configured.
# This avoids a crash on platforms (like Vercel) where pymysql is not installed.
db_engine = os.getenv("DB_ENGINE", "sqlite").lower()
database_url = os.getenv("DATABASE_URL", "")

if db_engine == "mysql" or database_url.startswith(("mysql://", "mysql+pymysql://")):
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass

