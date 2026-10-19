
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def test_connection():
    try:
        with psycopg.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            sslmode=os.environ["DB_SSLMODE"],
            connect_timeout=10,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), version();")
                result = cur.fetchone()

                print("Database connection successful!")
                print("Database:", result[0])
                print("PostgreSQL:", result[1].split(",")[0])

    except Exception as error:
        print("Database connection failed!")
        print("Error type:", type(error).__name__)


if __name__ == "__main__":
    test_connection()
