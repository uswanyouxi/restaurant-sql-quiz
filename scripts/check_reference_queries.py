"""Run the trusted five quiz SQL queries using the original restricted runner.

This checks PostgreSQL/permissions and the reference query syntax; it does NOT
make Gemini calls or by itself prove generated SQL correctness.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.knowledge import EXAMPLE_QUESTIONS
from sql_runner import execute_quiz_sql


def main():
    for question_id, (title, _question, reference_sql) in EXAMPLE_QUESTIONS.items():
        columns, rows = execute_quiz_sql(reference_sql)
        if not columns or not rows:
            raise RuntimeError(f"Q{question_id} returned no rows")
        print(f"Q{question_id}: {title} — PASS ({len(rows)} rows; {len(columns)} columns)")
    print("PASS: All five trusted reference queries execute with read-only access")


if __name__ == "__main__":
    main()
