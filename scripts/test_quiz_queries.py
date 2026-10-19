
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sql_runner import execute_quiz_sql


QUERIES = {
    "Q1 - Basic SELECT": """
        SELECT name, city
        FROM public.restaurants
        ORDER BY name;
    """,

    "Q2 - WHERE": """
        SELECT name, price
        FROM public.menu_items
        WHERE price > 15
        ORDER BY price DESC;
    """,

    "Q3 - JOIN": """
        SELECT r.name, m.name AS menu_item
        FROM public.restaurants AS r
        JOIN public.menu_items AS m
            ON r.id = m.restaurant_id
        ORDER BY r.name;
    """,

    "Q4 - GROUP BY": """
        SELECT restaurant_id, COUNT(*) AS total_orders
        FROM public.orders
        GROUP BY restaurant_id
        ORDER BY restaurant_id;
    """,

    "Q5 - Aggregate JOIN": """
        SELECT
            r.name,
            SUM(o.quantity * m.price) AS total_sales
        FROM public.orders AS o
        JOIN public.restaurants AS r
            ON o.restaurant_id = r.id
        JOIN public.menu_items AS m
            ON o.menu_item_id = m.id
        GROUP BY r.name
        ORDER BY total_sales DESC;
    """,
}


for label, sql in QUERIES.items():
    print(f"\n=== {label} ===")

    try:
        columns, rows = execute_quiz_sql(sql)

        print("PASS")
        print("Columns:", columns)
        print("Rows returned:", len(rows))

    except Exception as error:
        print("FAILED")
        print("Error type:", type(error).__name__)

        if type(error).__name__ == "UnsafeQueryError":
            print("Reason:", str(error))
