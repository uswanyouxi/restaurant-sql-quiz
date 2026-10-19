
import pytest

from sql_security import validate_sql, UnsafeQueryError


def test_valid_select():
    assert validate_sql("SELECT 1;") == "SELECT 1;"


def test_valid_restaurant_query():
    query = "SELECT name FROM restaurants;"
    assert validate_sql(query) == query


def test_empty_query():
    with pytest.raises(UnsafeQueryError):
        validate_sql("")


def test_insert_blocked():
    with pytest.raises(UnsafeQueryError):
        validate_sql("INSERT INTO restaurants (name) VALUES ('Test');")


def test_update_blocked():
    with pytest.raises(UnsafeQueryError):
        validate_sql("UPDATE restaurants SET name = 'Test';")


def test_delete_blocked():
    with pytest.raises(UnsafeQueryError):
        validate_sql("DELETE FROM restaurants;")


def test_multiple_statements_blocked():
    with pytest.raises(UnsafeQueryError):
        validate_sql("SELECT 1; SELECT 2;")


def test_drop_blocked():
    with pytest.raises(UnsafeQueryError):
        validate_sql("DROP TABLE restaurants;")



@pytest.mark.parametrize(
    "query",
    [
        "SELECT pg_sleep(1);",
        "SELECT pg_catalog.pg_sleep(1);",
        "SELECT * FROM public.quiz_submissions;",
        "SELECT expected_result FROM public.quiz_questions;",
        "SELECT * FROM auth.users;",
        "SELECT * FROM information_schema.tables;",
        "SELECT set_config('search_path', 'public', false);",
        "SELECT 1 INTO TEMP TABLE quiz_test;",
        "SELECT * FROM restaurants FOR UPDATE;",
    ],
)
def test_reject_unsafe_select_queries(query):
    with pytest.raises(UnsafeQueryError):
        validate_sql(query)
