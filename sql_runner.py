
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from sql_security import validate_sql

load_dotenv(Path(__file__).resolve().parent / ".env")

MAX_ROWS = 100


def execute_quiz_sql(sql: str):
    """Execute one read-only SQL query with a restricted user."""

    safe_sql = validate_sql(sql)

    connection_settings = {
        "host": os.environ["DB_HOST"],
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "postgres"),
        "user": os.environ["QUIZ_DB_USER"],
        "password": os.environ["QUIZ_DB_PASSWORD"],
        "sslmode": "require",
        "connect_timeout": 10,
    }

    
    with psycopg.connect(
        **connection_settings,
        autocommit=True,
    ) as conn:
        with conn.transaction():
            with conn.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute(
                    "SET LOCAL statement_timeout = '5000ms'"
                )

                cursor.execute(safe_sql)

                if cursor.description is None:
                    raise ValueError(
                        "The query did not return a result table."
                    )

                columns = [
                    column.name for column in cursor.description
                ]

                rows = cursor.fetchmany(MAX_ROWS + 1)

                if len(rows) > MAX_ROWS:
                    raise ValueError(
                        "Query returned more than 100 rows."
                    )

                return columns, rows
