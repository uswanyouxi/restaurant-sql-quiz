
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

connection_settings = {
    "host": os.environ["DB_HOST"],
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.environ["QUIZ_DB_USER"],
    "password": os.environ["QUIZ_DB_PASSWORD"],
    "sslmode": "require",
    "connect_timeout": 10,
}


def main():
    print("=== Quiz Runner Permission Check ===")

    with psycopg.connect(**connection_settings) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    current_user,
                    current_setting('default_transaction_read_only'),
                    has_table_privilege(
                        current_user, 'public.restaurants', 'SELECT'
                    ),
                    has_table_privilege(
                        current_user, 'public.restaurants', 'INSERT'
                    ),
                    has_table_privilege(
                        current_user, 'public.restaurants', 'UPDATE'
                    ),
                    has_table_privilege(
                        current_user, 'public.restaurants', 'DELETE'
                    ),
                    has_schema_privilege(
                        current_user, 'public', 'CREATE'
                    ),
                    has_schema_privilege(
                        current_user, 'auth', 'USAGE'
                    )
            """)

            result = cur.fetchone()

            print("Current user:", result[0])
            print("Default read-only:", result[1])
            print("Can SELECT restaurants:", result[2])
            print("Can INSERT restaurants:", result[3])
            print("Can UPDATE restaurants:", result[4])
            print("Can DELETE restaurants:", result[5])
            print("Can CREATE in public:", result[6])
            print("Can access auth schema:", result[7])


if __name__ == "__main__":
    main()
