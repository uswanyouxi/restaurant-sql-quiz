-- Create a read-only role for student SQL queries.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'quiz_reader'
    ) THEN
        CREATE ROLE quiz_reader NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO quiz_reader;

GRANT SELECT ON
    public.restaurants,
    public.menu_items,
    public.orders
TO quiz_reader;

SELECT
    grantee,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'quiz_reader'
  AND table_schema = 'public'
ORDER BY table_name, privilege_type;


-- Allow the quiz read-only role
-- to view business data through RLS.

CREATE POLICY "Quiz reader can view restaurants"
ON public.restaurants
FOR SELECT
TO quiz_reader
USING (true);

CREATE POLICY "Quiz reader can view menu items"
ON public.menu_items
FOR SELECT
TO quiz_reader
USING (true);

CREATE POLICY "Quiz reader can view orders"
ON public.orders
FOR SELECT
TO quiz_reader
USING (true);
