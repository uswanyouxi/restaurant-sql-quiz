
from pathlib import Path
import sys

# Allow imports from the project root.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sql_runner import execute_quiz_sql
from sql_security import UnsafeQueryError


def check_blocked(label, sql, expected_error):
    try:
        execute_quiz_sql(sql)

    except expected_error as error:
        print(f"PASS: {label} blocked")
        print(f"Error type: {type(error).__name__}")

    except Exception as error:
        print(f"FAIL: {label} raised an unexpected error")
        print(f"Error type: {type(error).__name__}")

    else:
        print(f"FAIL: {label} was NOT blocked")


print("=== SQL Security Tests ===")

# Test 1: DELETE must be blocked before execution.
check_blocked(
    "DELETE",
    "DELETE FROM public.restaurants;",
    UnsafeQueryError,
)

# Test 2: Multiple statements must be blocked.
check_blocked(
    "Multiple statements",
    "SELECT 1; SELECT 2;",
    UnsafeQueryError,
)

# Test 3: Hidden answers must not be readable.
check_blocked(
    "Hidden answers",
    "SELECT expected_sql FROM public.quiz_questions;",
    Exception,
)
