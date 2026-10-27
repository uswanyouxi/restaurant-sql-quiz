"""Curated non-sensitive knowledge retrieved through ChromaDB.

These descriptions mirror sql/schema.sql and the public five-question quiz.
We deliberately do not store credentials or protected user submissions.
"""

SCHEMA_DOCS = [
    (
        "schema_restaurants",
        "Database schema: public.restaurants(id INTEGER PRIMARY KEY, name VARCHAR(100), "
        "city VARCHAR(100)). Each row describes a restaurant. "
        "Use restaurants.id to order by restaurant ID.",
    ),
    (
        "schema_menu_items",
        "Database schema: public.menu_items(id INTEGER PRIMARY KEY, "
        "restaurant_id INTEGER REFERENCES public.restaurants(id), "
        "name VARCHAR(100), price NUMERIC(10,2)). "
        "The price is the price per individual menu item."
    ),
    (
        "schema_orders",
        "Database schema: public.orders(id INTEGER PRIMARY KEY, "
        "restaurant_id INTEGER REFERENCES public.restaurants(id), "
        "menu_item_id INTEGER REFERENCES public.menu_items(id), "
        "quantity INTEGER, order_date DATE). Each order row has a menu item and quantity."
    ),
    (
        "business_joins",
        "Business relationships: JOIN public.orders o with public.restaurants r "
        "ON o.restaurant_id = r.id; JOIN public.orders o with public.menu_items m "
        "ON o.menu_item_id = m.id. Always qualify ambiguous id/name columns."
    ),
    (
        "business_sales",
        "Business rules: line sales = orders.quantity * menu_items.price. "
        "Total revenue or total sales per restaurant = SUM(o.quantity * m.price) "
        "GROUP BY r.id, r.name; ORDER BY r.id. "
        "Use COUNT(*) for number of order rows."
    ),
]

# Reference examples are intentionally correct and only contain public business data.
EXAMPLE_QUESTIONS = {
    1: (
        "Basic SELECT",
        "Show all restaurant names and cities, ordered by restaurant ID.",
        "SELECT name, city FROM public.restaurants ORDER BY id;",
    ),
    2: (
        "WHERE and ORDER BY",
        "Show menu item names and prices above $15, sorted by price from highest to lowest.",
        "SELECT name, price FROM public.menu_items WHERE price > 15 ORDER BY price DESC, id;",
    ),
    3: (
        "COUNT and GROUP BY",
        "Count the number of orders for each restaurant ID, ordered by restaurant ID.",
        "SELECT restaurant_id, COUNT(*) AS order_count FROM public.orders "
        "GROUP BY restaurant_id ORDER BY restaurant_id;",
    ),
    4: (
        "JOIN",
        "Show each order ID and its menu item name, ordered by order ID.",
        "SELECT o.id, m.name FROM public.orders o JOIN public.menu_items m "
        "ON o.menu_item_id = m.id ORDER BY o.id;",
    ),
    5: (
        "JOIN and SUM",
        "Calculate total sales for each restaurant, showing the restaurant name "
        "and total sales ordered by restaurant ID.",
        "SELECT r.name AS restaurant_name, SUM(o.quantity * m.price) AS total_sales "
        "FROM public.restaurants r JOIN public.orders o ON r.id = o.restaurant_id "
        "JOIN public.menu_items m ON o.menu_item_id = m.id "
        "GROUP BY r.id, r.name ORDER BY r.id;",
    ),
}


def documents():
    """Return stable (id, document, metadata) rows used to build the vector index."""
    result = [(id_, text, {"type": "schema_or_rule"}) for id_, text in SCHEMA_DOCS]
    for qid, (title, question, sql) in EXAMPLE_QUESTIONS.items():
        result.append((
            f"example_question_{qid}",
            f"SQL quiz example Q{qid} ({title}). Question: {question} Reference SQL: {sql}",
            {"type": "few_shot_example", "question_id": qid},
        ))
    return result
