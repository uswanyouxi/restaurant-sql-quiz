
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

print("=== SQL Quiz Runner Security Test ===")

try:
    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["QUIZ_DB_USER"],
        password=os.environ["QUIZ_DB_PASSWORD"],
        sslmode="require",
        connect_timeout=10,
        options="-c statement_timeout=5000",
    ) as conn:

        # Test 1: Verify the connected role
        with conn.cursor() as cur:
            cur.execute("SELECT current_user;")
            print("Connected as:", cur.fetchone()[0])

        # Test 2: Read business data
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM public.restaurants;"
            )
            count = cur.fetchone()[0]
            print("Restaurant count:", count)

        # Test 3: Verify read-only permissions
        # SET LOCAL only applies to the current transaction.
        # Using EXPLAIN avoids executing a data modification.
        with conn.cursor() as cur:
            cur.execute(
                "SELECT has_table_privilege("
                "current_user, 'public.restaurants', 'INSERT');"
            )
            print("Can INSERT restaurants:", cur.fetchone()[0])

            cur.execute(
                "SELECT has_table_privilege("
                "current_user, 'public.restaurants', 'UPDATE');"
            )
            print("Can UPDATE restaurants:", cur.fetchone()[0])

            cur.execute(
                "SELECT has_table_privilege("
                "current_user, 'public.restaurants', 'DELETE');"
            )
            print("Can DELETE restaurants:", cur.fetchone()[0])

            cur.execute(
                "SELECT has_table_privilege("
                "current_user, 'public.quiz_questions', 'SELECT');"
            )
            print("Can read answer table:", cur.fetchone()[0])

        print("Security checks completed.")

except Exception as error:
    print("Connection or test failed!")
    print("Error type:", type(error).__name__)

    sqlstate = getattr(error, "sqlstate", None)

    if sqlstate:
        print("SQLSTATE:", sqlstate)
    else:
        print("SQLSTATE: Not available")

    # Do not print the raw error or connection string.
    print("Error details hidden to protect credentials.")


# Additional read-only checks
# This is a separate diagnostic test.

print("\n=== Additional Read-Only Tests ===")

try:
    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["QUIZ_DB_USER"],
        password=os.environ["QUIZ_DB_PASSWORD"],
        sslmode="require",
        connect_timeout=10,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SHOW default_transaction_read_only;")
            print("Default read-only:", cur.fetchone()[0])

            cur.execute("SHOW statement_timeout;")
            print("Statement timeout:", cur.fetchone()[0])

            cur.execute(
                "SELECT name, city "
                "FROM public.restaurants ORDER BY id;"
            )
            print("SELECT returned rows:", len(cur.fetchall()))

            cur.execute(
                "SELECT has_schema_privilege("
                "current_user, 'auth', 'USAGE');"
            )
            print("Can access auth schema:", cur.fetchone()[0])

except Exception as error:
    print("Additional test failed:", type(error).__name__)
