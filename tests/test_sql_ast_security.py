
import pytest

from sql_security import validate_sql, UnsafeQueryError


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM public.quiz_submissions;",
        "SELECT * FROM auth.users;",
        "SELECT * FROM pg_catalog.pg_tables;",
        "SELECT pg_sleep(1);",
        "SELECT 1 INTO TEMP TABLE test_table;",
        "SELECT * FROM public.restaurants FOR UPDATE;",
        "SELECT * FROM public.restaurants; DELETE FROM public.orders;",
        "WITH x AS (DELETE FROM public.orders RETURNING *) SELECT * FROM x;",
        "SELECT * FROM public.restaurants WHERE EXISTS (SELECT 1 FROM auth.users);",
    ],
)
def test_block_unsafe_ast_queries(query):
    with pytest.raises(UnsafeQueryError):
        validate_sql(query)


def test_allow_normal_cte():
    query = """
        WITH restaurant_counts AS (
            SELECT restaurant_id, COUNT(*) AS total
            FROM public.orders
            GROUP BY restaurant_id
        )
        SELECT * FROM restaurant_counts;
    """

    validate_sql(query)


def test_allow_normal_join():
    query = """
        SELECT r.name, COUNT(o.id)
        FROM public.restaurants r
        JOIN public.orders o
            ON r.id = o.restaurant_id
        GROUP BY r.name;
    """

    validate_sql(query)


def test_reject_schema_qualified_cte_name():
    query = """
        WITH restaurant_counts AS (
            SELECT COUNT(*) FROM public.orders
        )
        SELECT * FROM private.restaurant_counts;
    """
    with pytest.raises(UnsafeQueryError):
        validate_sql(query)


def test_reject_cte_shadowing_sensitive_table():
    query = """
        WITH quiz_submissions AS (
            SELECT id FROM public.restaurants
        )
        SELECT * FROM public.quiz_submissions;
    """
    with pytest.raises(UnsafeQueryError):
        validate_sql(query)
