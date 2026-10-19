
-- Step 5.2.2: Restricted question access

-- Remove any existing full-table SELECT privilege.
REVOKE SELECT ON TABLE public.quiz_questions
FROM quiz_reader, quiz_runner;

-- Grant access to public question fields only.
GRANT SELECT (
    id,
    title,
    description,
    points,
    hint
)
ON public.quiz_questions
TO quiz_reader;

-- Allow the read-only role to see question rows.
CREATE POLICY "Quiz reader public question access"
ON public.quiz_questions
FOR SELECT
TO quiz_reader
USING (true);
