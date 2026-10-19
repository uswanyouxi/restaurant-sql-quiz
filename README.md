
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
