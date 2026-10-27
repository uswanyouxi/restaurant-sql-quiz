"""Public restaurant schema, business rules and 5 SQL examples for RAG.

No credentials or private student answers are stored in this index.
This mirrors the committed sql/schema.sql and sql/seed.sql.
"""

SCHEMA_DOCS = [
    ("schema_restaurants",
     "PostgreSQL schema: public.restaurants has columns id INTEGER PRIMARY KEY, "
     "name VARCHAR(100), city VARCHAR(100). One row per restaurant. "
     "Order by restaurants.id when asked for restaurant ID order."),
    ("schema_menu_items",
     "PostgreSQL schema: public.menu_items has columns id INTEGER PRIMARY KEY, "
     "restaurant_id INTEGER REFERENCES public.restaurants(id), "
     "name VARCHAR(100), price NUMERIC(10,2). Price is the unit price."),
    ("schema_orders",
     "PostgreSQL schema: public.orders has columns id INTEGER PRIMARY KEY, "
     "restaurant_id INTEGER REFERENCES public.restaurants(id), "
     "menu_item_id INTEGER REFERENCES public.menu_items(id), "
     "quantity INTEGER, order_date DATE. Quantity is the number purchased."),
    ("business_relationships",
     "Relationships: public.orders.restaurant_id = public.restaurants.id; "
     "public.orders.menu_item_id = public.menu_items.id. "
     "Use aliases for ambiguous id and name columns."),
    ("business_sales",
     "Business rules: each order line total = o.quantity * m.price. "
     "Total sales per restaurant = SUM(o.quantity * m.price), grouped by "
     "r.id, r.name. Count order rows using COUNT(*).")
]

# Title, exact seeded question text, and trusted answer query.
EXAMPLES = {
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
    """Return id, text and metadata for 10 vector knowledge documents."""
    records = [(name, text, {"type": "schema_or_rule"})
               for name, text in SCHEMA_DOCS]
    for question_id, (title, question, sql) in EXAMPLES.items():
        records.append((
            f"sql_example_{question_id}",
            f"Quiz Q{question_id}: {title}. Natural language: {question} "
            f"Valid PostgreSQL SQL: {sql}",
            {"type": "few_shot_example", "question_id": question_id},
        ))
    return records
