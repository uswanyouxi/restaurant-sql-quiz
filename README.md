
# Restaurant Sales SQL Quiz

A web-based SQL quiz application built with Python, Streamlit, Supabase PostgreSQL, and Supabase Authentication.

## Features

- Five SQL quiz questions based on restaurant sales data.
- User sign-up and sign-in with Supabase Auth.
- Run SQL queries against a hosted PostgreSQL database.
- Display live query results in a table.
- Save SQL answers to Supabase.
- Row-Level Security (RLS) protects user submissions.
- Read-only database access and SQL query validation.
- Automated tests using pytest and GitHub Actions.

## Technology Stack

- Python 3.11
- Streamlit
- Supabase PostgreSQL
- Supabase Auth
- psycopg
- pandas
- pytest
- GitHub Actions

## Project Structure

- `app.py` - Main Streamlit application
- `auth.py` - User authentication
- `database.py` - Database connection
- `quiz.py` - Quiz question loading
- `sql_security.py` - SQL validation
- `sql_runner.py` - SQL execution
- `submissions.py` - Saving user answers
- `sql/` - Database schema, seed data, and roles
- `tests/` - Automated tests
- `scripts/` - Database and integration test scripts
- `.github/workflows/ci.yml` - Continuous integration workflow

## Local Setup

1. Clone the repository.

2. Create a Python virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the environment.

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Create a Supabase project and configure the database using the SQL files in `sql/`.

6. Copy `.env.example` to `.env` and fill in the required Supabase and database credentials.

7. Start the Streamlit application:

   ```bash
   streamlit run app.py
   ```

## How to Use

1. Open the application.
2. Sign up or sign in.
3. Select one of the five SQL questions.
4. Write a SQL SELECT query.
5. Click **Run SQL** to view the live result.
6. Click **Save Answer** to store your submission.

## Database Security

The application uses a restricted PostgreSQL role for quiz queries.

- Student queries run in read-only transactions.
- SQL statements are validated before execution.
- Only approved restaurant data tables are available.
- Database permissions restrict modification operations.
- Supabase RLS restricts access to saved submissions.
- Users can only read and submit answers under their own authenticated identity.

SQL validation and database permissions are defense-in-depth controls, not a guarantee that arbitrary SQL is safe.

## Testing

Run unit tests:

```bash
python -m pytest tests/ -v
```

Database integration tests are available in the `scripts/` directory.

## Continuous Integration

GitHub Actions automatically runs Python tests and database permission checks.

Database connection credentials are configured using GitHub Actions Secrets rather than committed to the repository.

## Deployment

The application is intended to be deployed using Streamlit Community Cloud.

Deployment URL: https://restaurant-sql-quiz-8agvlli4ykngs9sc2piica.streamlit.app

## Notes

- Never commit `.env` or database passwords.
- Use a restricted PostgreSQL user for student SQL queries.
- Supabase authentication is required before executing or saving SQL.

## Week 8: RAG-Powered Text-to-SQL

This extension uses a real Retrieval-Augmented Generation pipeline:

1. User chooses or edits a natural-language restaurant SQL question.
2. ChromaDB persists and retrieves relevant embedded schema documentation,
   business rules and SQL few-shot examples with vector similarity search.
3. Google Gemini AI API receives only the question plus retrieved Chroma context
   and generates PostgreSQL SQL code.
4. SQL is automatically evaluated by the existing restricted read-only runner.
5. For an unmodified quiz question, the generated query's result is compared
   with a trusted reference SQL query (without accessing protected answers).

### Technology and architecture

- Database: Supabase PostgreSQL (restaurants, menu_items, orders).
- Vector store: ChromaDB PersistentClient; 10 embedded knowledge documents
  in rag/knowledge.py; collection.query() performs real vector retrieval.
- AI API: Google Gemini via google-genai; default model gemini-2.5-flash.
- App: original Streamlit quiz plus a new RAG generator section.
- Security: existing AST query validation, allowlisted tables/functions, and
  a read-only PostgreSQL role with a timeout and a 100-row cap.
- Bonus: automatic SQL execution/result table and reference result validation
  (using the same restricted read-only runner; no elevated answer access).

### Setup and local run

Use Python 3.11. Follow original Supabase setup instructions above,
activate your local virtual environment, then install dependencies:

    python -m pip install -r requirements.txt

Create a Gemini key in Google AI Studio: https://aistudio.google.com/app/apikey

Keep it private in your local .env file (never in GitHub):

    GEMINI_API_KEY=YOUR_PRIVATE_KEY
    GEMINI_MODEL=gemini-2.5-flash

Run the tests and the real vector retrieval smoke test:

    python -m pytest tests/ -v
    python scripts/check_rag_index.py

Start the app:

    python -m streamlit run app.py

Sign in with the original account. In the RAG section choose a quiz
question, click Generate SQL with RAG, inspect the retrieved knowledge and
generated SQL, and review the automatic SQL execution and validation.

### Deploying to Streamlit Cloud

The original deployment URL remains:
https://restaurant-sql-quiz-8agvlli4ykngs9sc2piica.streamlit.app/

This is still the original main-branch deployment until Week 8 is tested
and merged. After verifying this development branch, set GEMINI_API_KEY
under Streamlit Cloud app Settings > Secrets. Keep existing Supabase secrets.
Then merge week8-rag to main and verify the deployed app in an incognito browser.
Cloud storage is ephemeral, so Chroma rebuilds its index from source on startup.
Its first embedding-model initialization may require network access and time.

### Screenshots required for submission

Capture REAL screenshots from your running application and add them to
screenshots/ and embed them below before submitting:

- rag_basic.png: natural-language question, generated SQL, retrieved context.
- rag_bonus.png: automatically executed SQL, result table, validation status.

Do not commit .env, passwords, Gemini keys or tokens to this repository.
A student/grader should be able to open the deployed app, log in,
ask a quiz question and receive AI-generated SQL code.

### Testing

- Existing 30 SQL security tests are preserved.
- Additional tests/test_rag.py verifies knowledge, grounded prompts and
  bonus result validation without relying on live API credentials.
- scripts/check_rag_index.py verifies actual Chroma vector storage and query.
- Real online end-to-end validation and screenshots are still needed.

