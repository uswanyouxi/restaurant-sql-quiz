
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def get_questions():
    """Read public quiz questions from PostgreSQL."""

    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["QUIZ_DB_USER"],
        password=os.environ["QUIZ_DB_PASSWORD"],
        sslmode="require",
        connect_timeout=10,
        row_factory=dict_row,
    ) as conn:

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    title,
                    description,
                    points,
                    hint
                FROM public.quiz_questions
                ORDER BY id;
            """)

            return cur.fetchall()


def format_question_label(question):
    return (
        f"Q{question['id']}: "
        f"{question['title']} "
        f"({question['points']} points)"
    )
