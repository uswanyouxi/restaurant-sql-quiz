
import streamlit as st
import pandas as pd

from auth import (
    sign_up,
    sign_in,
    sign_out,
    validate_session,
)
from quiz import get_questions, format_question_label
from sql_runner import execute_quiz_sql
from sql_security import UnsafeQueryError
from submissions import save_answer


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Restaurant SQL Quiz",
    page_icon="🍽️",
    layout="wide",
)

st.title("🍽️ Restaurant Sales SQL Quiz")
st.caption(
    "Practice SQL with real restaurant data "
    "stored in Supabase PostgreSQL."
)


# ============================================================
# Authentication
# ============================================================

if "auth_session" not in st.session_state:
    st.session_state.auth_session = None

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None


def clear_auth():
    """Remove the user's local authentication state."""
    st.session_state.auth_session = None
    st.session_state.auth_user = None


def verify_login():
    """Verify the user's session with Supabase Auth."""
    session = st.session_state.auth_session

    if session is None:
        clear_auth()
        return False

    try:
        valid_session, user = validate_session(
            session.access_token,
            session.refresh_token,
        )

        if user is None:
            clear_auth()
            return False

        st.session_state.auth_session = valid_session
        st.session_state.auth_user = user

        return True

    except Exception:
        clear_auth()
        return False


if st.session_state.auth_session is not None:
    verify_login()


# ============================================================
# Sign In / Sign Up
# ============================================================

if st.session_state.auth_user is None:
    st.warning("Please sign in to use the SQL Quiz.")

    tab_sign_in, tab_sign_up = st.tabs(
        ["Sign In", "Sign Up"]
    )

    with tab_sign_in:
        with st.form("sign_in_form"):
            email = st.text_input(
                "Email",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            login_button = st.form_submit_button(
                "Sign In"
            )

        if login_button:
            if not email.strip() or not password:
                st.error(
                    "Please enter your email and password."
                )

            else:
                try:
                    response = sign_in(
                        email.strip(),
                        password,
                    )

                    if response.session and response.user:
                        st.session_state.auth_session = (
                            response.session
                        )
                        st.session_state.auth_user = (
                            response.user
                        )
                        st.rerun()

                    else:
                        st.error("Sign in failed.")

                except Exception:
                    st.error(
                        "Sign in failed. Check your email, "
                        "password, and email confirmation."
                    )

    with tab_sign_up:
        with st.form("sign_up_form"):
            new_email = st.text_input(
                "Email",
                key="signup_email",
            )

            new_password = st.text_input(
                "Password",
                type="password",
                key="signup_password",
            )

            signup_button = st.form_submit_button(
                "Create Account"
            )

        if signup_button:
            if not new_email.strip() or not new_password:
                st.error(
                    "Please enter your email and password."
                )

            else:
                try:
                    response = sign_up(
                        new_email.strip(),
                        new_password,
                    )

                    if response.user:
                        st.success(
                            "Registration request received. "
                            "Please check your email for "
                            "a confirmation link, "
                            "then return to sign in."
                        )

                    else:
                        st.warning(
                            "Registration could not be confirmed. "
                            "Please check your account status."
                        )

                except Exception:
                    st.error(
                        "Registration could not be completed."
                    )

    # Block all quiz functions when signed out.
    st.stop()


# ============================================================
# Authenticated user area
# ============================================================

st.success(
    f"Signed in as: {st.session_state.auth_user.email}"
)

if st.button("Sign Out"):
    session = st.session_state.auth_session

    try:
        if session is not None:
            sign_out(
                session.access_token,
                session.refresh_token,
            )
    except Exception:
        pass

    clear_auth()
    st.rerun()


st.divider()


# ============================================================
# Load quiz questions from PostgreSQL
# ============================================================

st.subheader("SQL Quiz Questions")

try:
    questions = get_questions()

except Exception:
    st.error(
        "Could not load quiz questions from PostgreSQL. "
        "Please check your database connection."
    )
    st.stop()


if not questions:
    st.warning("No quiz questions are available.")
    st.stop()


# ============================================================
# Select a question
# ============================================================

question_options = {
    format_question_label(question): question
    for question in questions
}

selected_label = st.selectbox(
    "Select a question:",
    options=list(question_options.keys()),
)

selected_question = question_options[selected_label]

st.markdown(
    f"### {selected_question['title']}"
)

st.write(selected_question["description"])

st.info(
    f"Points: {selected_question['points']}"
)

if selected_question.get("hint"):
    with st.expander("Show Hint"):
        st.write(selected_question["hint"])


st.divider()


# ============================================================
# SQL editor
# ============================================================

st.subheader("Write Your SQL Query")

st.caption(
    "Use SELECT queries to explore the restaurant data. "
    "Available tables: restaurants, menu_items, orders."
)

sql_input = st.text_area(
    "SQL Query",
    value="",
    height=180,
    placeholder=(
        "SELECT name, city\n"
        "FROM public.restaurants\n"
        "ORDER BY id;"
    ),
    key=f"sql_editor_{selected_question['id']}",
)


# ============================================================
# Run SQL and Save Answer buttons
# ============================================================

col_run, col_save = st.columns(
    [1, 1],
    gap="small",
)

with col_run:
    run_button = st.button(
        "Run SQL",
        type="primary",
        use_container_width=True,
    )

with col_save:
    save_button = st.button(
        "Save Answer",
        use_container_width=True,
    )


# ============================================================
# Run SQL
# ============================================================

if run_button:
    if not verify_login():
        st.error(
            "Your session has expired. "
            "Please sign in again."
        )
        st.stop()

    if not sql_input.strip():
        st.warning(
            "Please enter a SQL query before running it."
        )

    else:
        try:
            with st.spinner("Running SQL query..."):
                columns, rows = execute_quiz_sql(
                    sql_input
                )

            result_df = pd.DataFrame(
                rows,
                columns=columns,
            )

            st.success(
                "SQL query executed successfully."
            )

            st.subheader("Query Results")

            st.dataframe(
                result_df,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                f"Returned {len(rows)} rows."
            )

        except UnsafeQueryError as error:
            st.error(
                f"SQL not allowed: {error}"
            )

        except Exception:
            st.error(
                "Query execution failed. "
                "Please check your SQL syntax, "
                "table names, and column names."
            )


# ============================================================
# Save Answer
# ============================================================

if save_button:
    if not verify_login():
        st.error(
            "Your session has expired. "
            "Please sign in again."
        )
        st.stop()

    if not sql_input.strip():
        st.warning(
            "Please write a SQL answer before saving."
        )

    else:
        try:
            session = st.session_state.auth_session

            with st.spinner("Saving your answer..."):
                saved_data = save_answer(
                    access_token=session.access_token,
                    refresh_token=session.refresh_token,
                    question_id=selected_question["id"],
                    submitted_sql=sql_input,
                )

            st.success(
                "Your answer was saved successfully!"
            )

            st.info(
                f"Saved answer for "
                f"Question {selected_question['id']}."
            )

        except ValueError as error:
            st.error(str(error))

        except Exception:
            st.error(
                "Could not save your answer. "
                "Please check your login session "
                "and Supabase permissions."
            )


st.divider()

st.caption(
    "Restaurant SQL Quiz | "
    "Supabase PostgreSQL | "
    "Supabase Authentication"
)
