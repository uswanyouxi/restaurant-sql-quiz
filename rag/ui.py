"""Streamlit RAG UI; imported only after the existing user has authenticated."""
import pandas as pd
import streamlit as st

from rag.generator import generate_sql, get_api_key
from rag.vector_store import initialize_index, retrieve_context
from rag.validation import validate_against_reference
from sql_runner import execute_quiz_sql
from sql_security import UnsafeQueryError


@st.cache_resource(show_spinner="Initializing ChromaDB knowledge vectors...")
def get_cached_index():
    return initialize_index()


def render_rag_section(questions):
    st.header("🤖 RAG-Powered Text-to-SQL")
    st.caption("Question → ChromaDB vector retrieval → Gemini AI → PostgreSQL SQL")

    options = {f"Q{q['id']}: {q['title']}": q for q in questions}
    label = st.selectbox("Choose a quiz question", list(options), key="rag_question_selector")
    selected = options[label]
    with st.form("rag_query_form"):
        custom = st.text_area(
            "Question (you can edit it)",
            value=selected["description"],
            key=f"rag_question_text_{selected['id']}",
            height=110,
            help="The selected quiz question has a known reference answer for validation.",
        )
        submitted = st.form_submit_button("✨ Generate SQL with RAG", type="primary")

    if submitted:
        st.session_state.pop("rag_last_output", None)
        if not custom.strip():
            st.warning("Enter a natural-language question first.")
        elif len(custom) > 2000:
            st.error("Question too long (maximum 2,000 characters).")
        elif not get_api_key():
            st.error("Configure GEMINI_API_KEY in your .env or Streamlit Cloud secrets first.")
        else:
            try:
                with st.spinner("Searching ChromaDB and generating SQL..."):
                    collection = get_cached_index()
                    retrieved = retrieve_context(collection, custom, top_k=5)
                    sql = generate_sql(custom, retrieved)
                record = {
                    "question_id": selected["id"],
                    "asked": custom,
                    "reference_question": selected["description"],
                    "sql": sql,
                    "retrieved": retrieved,
                    "columns": None,
                    "rows": None,
                    "execution_error": None,
                    "validation": None,
                }
                # Bonus: automatic, read-only execution and automatic validation.
                try:
                    with st.spinner("Automatically executing and validating SQL..."):
                        columns, rows = execute_quiz_sql(sql)
                        record["columns"], record["rows"] = columns, rows
                        if custom.strip() == selected["description"].strip():
                            record["validation"] = validate_against_reference(
                                selected["id"], columns, rows, execute_quiz_sql
                            )
                except UnsafeQueryError as error:
                    record["execution_error"] = f"Blocked by SQL safety rules: {error}"
                except Exception:
                    # Avoid exposing DB hostnames, SQL connection details, or tokens.
                    record["execution_error"] = "Query or validation failed; check generated SQL and database access."
                st.session_state["rag_last_output"] = record
            except Exception as error:
                st.error(f"RAG request failed: {type(error).__name__}: {error}")

    record = st.session_state.get("rag_last_output")
    if record:
        st.subheader("AI-generated SQL")
        st.code(record["sql"], language="sql")
        st.success("Full pipeline completed: question → vector retrieval → LLM → SQL")
        with st.expander("Retrieved knowledge from ChromaDB (actual vector search)"):
            for index, item in enumerate(record["retrieved"], 1):
                st.markdown(f"**{index}. {item['id']}** (distance: {item['distance']:.3f})")
                st.write(item["text"])

        st.subheader("Bonus: Automatic SQL execution")
        if record["execution_error"]:
            st.warning(f"SQL was not executed: {record['execution_error']}")
        elif record["rows"] is not None:
            st.dataframe(
                pd.DataFrame(record["rows"], columns=record["columns"]),
                use_container_width=True, hide_index=True,
            )
            st.caption(f"Returned {len(record['rows'])} rows (read-only).")
            st.subheader("Bonus: Automatic result validation")
            if record["validation"] is True:
                st.success("Correct: matches the trusted reference result.")
            elif record["validation"] is False:
                st.error("Incorrect: generated result differs from the reference.")
            else:
                st.info("Validation unavailable for a modified/custom question.")
    st.divider()
