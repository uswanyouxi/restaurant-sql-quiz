
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

This project extends the existing PostgreSQL SQL Quiz with a real retrieval-augmented
SQL generator. The original sign-in, SQL editor, safe query runner and Save Answer
features remain unchanged.

### Live application

[Deployed Streamlit website](https://restaurant-sql-quiz-8agvlli4ykngs9sc2piica.streamlit.app/)

**Note:** The deployed RAG feature is available only after merging this branch into
`main`, adding its `GEMINI_API_KEY` to the Streamlit application's secrets, and
redeploying successfully. The link itself is the existing Week 7 website until then.

### Architecture and AI API

`Natural-language question → ChromaDB vector similarity search → retrieved
schema/rules/SQL examples → Gemini API → PostgreSQL SELECT SQL → optional automatic
read-only execution → result comparison with trusted SQL reference`

- PostgreSQL / Supabase stores the restaurant, menu, orders and quiz data.
- ChromaDB is a **real vector database** that embeds and stores 10 knowledge
  documents from `rag/knowledge.py` and retrieves relevant text with
  `collection.query(query_texts=[...])`.
- Chroma uses its default local embedding model; an ONNX model may be downloaded
  on first initialization. `.chroma/` is local and ignored by Git. On cold cloud
  start, `initialize_index()` recreates its vector collection from source files.
- Google Gemini is called using the `google-genai` SDK and receives only the
  user question plus the top five Chroma retrieval results.
- `execute_quiz_sql()` executes generated SQL only after AST validation, as
  `quiz_runner`, in a read-only transaction with time/row limits.
- Bonus validation executes a predefined correct reference SELECT using the
  **same restricted runner**, comparing column labels and normalized values.
  It does not grant access to protected `expected_result` columns. Comparison
  disregards physical result-row order and checks result-equivalence only.

### Local setup

1. Clone the repo, use Python 3.11, activate a virtual environment and install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

2. Set up Supabase as described above. Add your own Gemini key locally to `.env`:

   ```text
   GEMINI_API_KEY=YOUR_PRIVATE_KEY
   GEMINI_MODEL=gemini-2.5-flash
   ```

   Create a key in [Google AI Studio](https://aistudio.google.com/app/apikey).
   **Never commit real keys or `.env`**. Billing and rate limits depend on your
   model, project and account, not your ChatGPT subscription.

3. Verify the vector index and run all tests:

   ```powershell
   python scripts/check_rag_index.py
   python -m pytest tests/ -v
   ```

4. Start the app and sign in with an existing account:

   ```powershell
   python -m streamlit run app.py
   ```

5. Choose an existing quiz question in the RAG section, click **Generate SQL
   with RAG**, and examine the generated SQL and *Retrieved knowledge* expander.
   The app automatically tries to execute generated SQL safely; for an unchanged
   quiz question it compares the result with that question's trusted reference.

### Streamlit Cloud deployment

1. Push and merge `week8-rag` into `main` only after testing.
2. Open Streamlit Cloud → your app → Settings → Secrets and add
   `GEMINI_API_KEY="..."` (and optionally `GEMINI_MODEL="gemini-2.5-flash"`).
3. Existing Supabase secrets/credentials stay as configured. Restart/redeploy.
4. Test from a logged-out/incognito browser with a valid test login.
5. Ensure the Supabase free project is not paused when it is graded.

### Evidence and screenshots

Before submission capture and embed real screenshots (do not fabricate outputs):

- `screenshots/rag_basic.png` — natural language question, real AI-generated SQL,
  and retrieved-knowledge expander showing actual vector results.
- `screenshots/rag_bonus.png` — generated SQL, automatically executed result table,
  and a correct/incorrect validation status.

After capturing, add links to those images in this README, commit, and verify
that the images render on GitHub. Do not show any passwords, API keys or tokens.

### Automated checks

`tests/test_rag.py` tests knowledge creation, prompt grounding, SQL formatting,
and result validation without contacting an AI API. The original 30 SQL-security
tests remain intact. The smoke test in `scripts/check_rag_index.py` additionally
checks real ChromaDB embedding, storage and similarity search.

