
-- Restaurant Sales SQL Quiz
-- Step 3.2: Seed restaurants and menu items

INSERT INTO public.restaurants (id, name, city)
VALUES
    (1, 'Blue Devil Bistro', 'Durham'),
    (2, 'Oak City Grill', 'Raleigh'),
    (3, 'Bull City Pizza', 'Durham'),
    (4, 'Carolina Kitchen', 'Cary'),
    (5, 'Triangle Sushi', 'Chapel Hill');

INSERT INTO public.menu_items
    (id, restaurant_id, name, price)
VALUES
    (1, 1, 'Cheeseburger', 14.00),
    (2, 1, 'Grilled Chicken', 18.00),
    (3, 1, 'Caesar Salad', 11.00),

    (4, 2, 'BBQ Ribs', 24.00),
    (5, 2, 'Steak Sandwich', 19.00),
    (6, 2, 'French Fries', 6.00),

    (7, 3, 'Pepperoni Pizza', 16.00),
    (8, 3, 'Margherita Pizza', 15.00),
    (9, 3, 'Garlic Bread', 7.00),

    (10, 4, 'Fried Chicken', 17.00),
    (11, 4, 'Mac and Cheese', 12.00),
    (12, 4, 'Sweet Tea', 4.00),

    (13, 5, 'Salmon Roll', 13.00),
    (14, 5, 'Sushi Combo', 25.00),
    (15, 5, 'Miso Soup', 5.00);




-- Insert 30 orders


INSERT INTO public.orders
    (id, restaurant_id, menu_item_id, quantity, order_date)
VALUES
    (1, 1, 1, 2, '2026-10-01'),
    (2, 1, 2, 1, '2026-10-01'),
    (3, 1, 3, 3, '2026-10-02'),
    (4, 1, 1, 1, '2026-10-03'),
    (5, 1, 2, 2, '2026-10-04'),
    (6, 1, 3, 1, '2026-10-05'),

    (7, 2, 4, 1, '2026-10-01'),
    (8, 2, 5, 2, '2026-10-02'),
    (9, 2, 6, 3, '2026-10-03'),
    (10, 2, 4, 2, '2026-10-04'),
    (11, 2, 5, 1, '2026-10-05'),
    (12, 2, 6, 2, '2026-10-06'),

    (13, 3, 7, 2, '2026-10-01'),
    (14, 3, 8, 1, '2026-10-02'),
    (15, 3, 9, 3, '2026-10-03'),
    (16, 3, 7, 1, '2026-10-04'),
    (17, 3, 8, 2, '2026-10-05'),
    (18, 3, 9, 2, '2026-10-06'),

    (19, 4, 10, 2, '2026-10-01'),
    (20, 4, 11, 1, '2026-10-02'),
    (21, 4, 12, 4, '2026-10-03'),
    (22, 4, 10, 1, '2026-10-04'),
    (23, 4, 11, 2, '2026-10-05'),
    (24, 4, 12, 2, '2026-10-06'),

    (25, 5, 13, 2, '2026-10-01'),
    (26, 5, 14, 1, '2026-10-02'),
    (27, 5, 15, 3, '2026-10-03'),
    (28, 5, 13, 1, '2026-10-04'),
    (29, 5, 14, 2, '2026-10-05'),
    (30, 5, 15, 2, '2026-10-06');



-- Insert 5 SQL quiz questions


INSERT INTO public.quiz_questions
    (id, title, description, points, hint,
     expected_sql, expected_result)
VALUES
(
    1,
    'Basic SELECT',
    'Show all restaurant names and cities, ordered by restaurant ID.',
    4,
    'Use SELECT to choose columns and ORDER BY id.',
    'SELECT name, city FROM public.restaurants ORDER BY id;',
    '[]'::jsonb
),
(
    2,
    'WHERE and ORDER BY',
    'Show menu item names and prices above $15, sorted by price from highest to lowest.',
    4,
    'Use WHERE price > 15 and ORDER BY price DESC.',
    'SELECT name, price FROM public.menu_items WHERE price > 15 ORDER BY price DESC, id;',
    '[]'::jsonb
),
(
    3,
    'COUNT and GROUP BY',
    'Count the number of orders for each restaurant ID, ordered by restaurant ID.',
    4,
    'Use COUNT(*) and GROUP BY restaurant_id.',
    'SELECT restaurant_id, COUNT(*) AS order_count FROM public.orders GROUP BY restaurant_id ORDER BY restaurant_id;',
    '[]'::jsonb
),
(
    4,
    'JOIN',
    'Show each order ID and its menu item name, ordered by order ID.',
    4,
    'Join orders and menu_items using menu_item_id and id.',
    'SELECT o.id, m.name FROM public.orders o JOIN public.menu_items m ON o.menu_item_id = m.id ORDER BY o.id;',
    '[]'::jsonb
),
(
    5,
    'JOIN and SUM',
    'Calculate total sales for each restaurant, showing the restaurant name and total sales ordered by restaurant ID.',
    4,
    'Join restaurants, orders and menu_items. Use SUM(quantity * price) and GROUP BY.',
    'SELECT r.name AS restaurant_name, SUM(o.quantity * m.price) AS total_sales FROM public.restaurants r JOIN public.orders o ON r.id = o.restaurant_id JOIN public.menu_items m ON o.menu_item_id = m.id GROUP BY r.id, r.name ORDER BY r.id;',
    '[]'::jsonb
);

-- Generate expected results from live database data.
UPDATE public.quiz_questions
SET expected_result = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'name', r.name,
            'city', r.city
        ) ORDER BY r.id
    )
    FROM public.restaurants r
)
WHERE id = 1;

UPDATE public.quiz_questions
SET expected_result = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'name', m.name,
            'price', m.price
        ) ORDER BY m.price DESC, m.id
    )
    FROM public.menu_items m
    WHERE m.price > 15
)
WHERE id = 2;

UPDATE public.quiz_questions
SET expected_result = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'restaurant_id', x.restaurant_id,
            'order_count', x.order_count
        ) ORDER BY x.restaurant_id
    )
    FROM (
        SELECT restaurant_id, COUNT(*) AS order_count
        FROM public.orders
        GROUP BY restaurant_id
    ) x
)
WHERE id = 3;

UPDATE public.quiz_questions
SET expected_result = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'id', o.id,
            'name', m.name
        ) ORDER BY o.id
    )
    FROM public.orders o
    JOIN public.menu_items m
        ON o.menu_item_id = m.id
)
WHERE id = 4;

UPDATE public.quiz_questions
SET expected_result = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'restaurant_name', x.restaurant_name,
            'total_sales', x.total_sales
        ) ORDER BY x.restaurant_id
    )
    FROM (
        SELECT
            r.id AS restaurant_id,
            r.name AS restaurant_name,
            SUM(o.quantity * m.price) AS total_sales
        FROM public.restaurants r
        JOIN public.orders o
            ON r.id = o.restaurant_id
        JOIN public.menu_items m
            ON o.menu_item_id = m.id
        GROUP BY r.id, r.name
    ) x
)
WHERE id = 5;
