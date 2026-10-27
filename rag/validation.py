"""Bonus: compare AI result with a trusted reference query, read-only."""
from collections import Counter
from datetime import date, datetime
from decimal import Decimal

from rag.knowledge import EXAMPLE_QUESTIONS


def _normalize(value):
    if isinstance(value, Decimal):
        return ("number", str(value.normalize()))
    if isinstance(value, bool):
        return ("bool", str(value))
    if isinstance(value, (int, float)):
        return ("number", str(Decimal(str(value)).normalize()))
    if isinstance(value, (datetime, date)):
        return ("date", value.isoformat())
    if value is None:
        return ("none", "")
    return ("text", str(value))


def compare_results(actual_columns, actual_rows, expected_columns, expected_rows):
    """Compare column labels and row values, ignoring only row ordering."""
    if [x.lower() for x in actual_columns] != [x.lower() for x in expected_columns]:
        return False
    actual = Counter(tuple(_normalize(v) for v in row) for row in actual_rows)
    expected = Counter(tuple(_normalize(v) for v in row) for row in expected_rows)
    return actual == expected


def validate_against_reference(question_id, actual_columns, actual_rows, execute):
    """Execute the trusted SQL through *the same restricted read-only runner*.

    No elevated database user and no access to protected expected_result fields.
    """
    entry = EXAMPLE_QUESTIONS.get(int(question_id))
    if not entry:
        return None
    expected_columns, expected_rows = execute(entry[2])
    return compare_results(actual_columns, actual_rows, expected_columns, expected_rows)
