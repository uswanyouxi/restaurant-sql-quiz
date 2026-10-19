-- Create a dedicated login role for the quiz.

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'quiz_runner'
    ) THEN
        CREATE ROLE quiz_runner
            LOGIN
            PASSWORD NULL
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION;
    END IF;
END
$$;

-- Grant only the read-only permissions.
GRANT quiz_reader TO quiz_runner;

-- Prevent this role from creating objects in public.
REVOKE CREATE ON SCHEMA public FROM quiz_runner;

-- Set limits for quiz queries.
ALTER ROLE quiz_runner SET statement_timeout = '5s';
ALTER ROLE quiz_runner SET default_transaction_read_only = on;