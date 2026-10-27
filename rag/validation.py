"""Bonus result validator with a trusted reference and a read-only runner."""
from collections import Counter
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from rag.knowledge import EXAMPLES


def normalize(value):
    if value is None:
        return ("null", "")
    if isinstance(value, bool):
        return ("boolean", str(value))
    if isinstance(value, (Decimal, int, float)):
        try:
            return ("number", str(Decimal(str(value)).normalize()))
        except InvalidOperation:
            return ("number", str(value))
    if isinstance(value, (date, datetime)):
        return ("date", value.isoformat())
    return ("text", str(value))


def compare_results(actual_cols, actual_rows, expected_cols, expected_rows):
    """Compare columns and multisets of rows; ignore only physical row order."""
    if [str(x).lower() for x in actual_cols] != [
        str(x).lower() for x in expected_cols
    ]:
        return False
    actual = Counter(tuple(normalize(v) for v in row) for row in actual_rows)
    expected = Counter(tuple(normalize(v) for v in row) for row in expected_rows)
    return actual == expected


def validate_against_reference(question_id, actual_columns, actual_rows, execute):
    """Never fetch protected quiz answer fields or elevate SQL privileges."""
    example = EXAMPLES.get(int(question_id))
    if example is None:
        return None
    expected_columns, expected_rows = execute(example[2])
    return compare_results(
        actual_columns, actual_rows, expected_columns, expected_rows
    )
