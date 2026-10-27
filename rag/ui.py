"""User interface for vector retrieval, SQL generation and two bonus features."""
import pandas as pd
import streamlit as st

from rag.generator import generate_sql, get_api_key
from rag.vector_store import initialize_index, retrieve_context
from rag.validation import validate_against_reference
from sql_runner import execute_quiz_sql
from sql_security import UnsafeQueryError


@st.cache_resource(show_spinner="Initializing ChromaDB vector knowledge index...")
def get_cached_index():
    return initialize_index()


def render_rag_section(questions):
    st.header("🤖 RAG-Powered Text-to-SQL")
    st.caption("Natural-language question → ChromaDB → Gemini → Generated SQL")

    options = {f"Q{q['id']}: {q['title']}": q for q in questions}
    label = st.selectbox(
        "Choose a SQL Quiz question for AI generation",
        list(options),
        key="rag_question_selector",
    )
    selected = options[label]
    with st.form("rag_generator_form"):
        question = st.text_area(
            "Natural-language SQL question (editable)",
            value=selected["description"],
            key=f"rag_text_{selected['id']}",
            height=105,
        )
        clicked = st.form_submit_button(
            "✨ Generate SQL with RAG", type="primary"
        )

    if clicked:
        st.session_state.pop("rag_latest", None)
        if not question.strip():
            st.warning("Enter a question first.")
        elif len(question) > 2000:
            st.error("Question is too long (2,000 character limit).")
        elif not get_api_key():
            st.error("GEMINI_API_KEY is not configured.")
        else:
            try:
                with st.spinner("Retrieving knowledge and generating SQL..."):
                    collection = get_cached_index()
                    retrieved = retrieve_context(collection, question, top_k=5)
                    sql = generate_sql(question, retrieved)
                result = {
                    "sql": sql,
                    "retrieved": retrieved,
                    "columns": None,
                    "rows": None,
                    "error": None,
                    "validation": None,
                }
                try:
                    with st.spinner("Executing SQL in read-only mode..."):
                        columns, rows = execute_quiz_sql(sql)
                        result["columns"], result["rows"] = columns, rows
                        if question.strip() == selected["description"].strip():
                            result["validation"] = validate_against_reference(
                                selected["id"], columns, rows, execute_quiz_sql
                            )
                except UnsafeQueryError as exc:
                    result["error"] = f"Unsafe query blocked: {exc}"
                except Exception:
                    result["error"] = (
                        "Read-only SQL execution or validation failed. "
                        "Review SQL syntax and database connectivity."
                    )
                st.session_state["rag_latest"] = result
            except Exception:
                st.error(
                    "RAG generation failed. Check API key, Gemini quota, "
                    "ChromaDB initialization and internet connectivity."
                )

    result = st.session_state.get("rag_latest")
    if result:
        st.subheader("Generated SQL")
        st.code(result["sql"], language="sql")
        st.success("RAG pipeline complete: Question → Vector Retrieval → AI → SQL")
        with st.expander("Actual ChromaDB Retrieved Knowledge"):
            for i, record in enumerate(result["retrieved"], start=1):
                st.markdown(
                    f"**{i}. {record['id']}** (distance: {record['distance']:.3f})"
                )
                st.write(record["text"])

        st.subheader("Bonus: Automatic SQL Execution")
        if result["error"]:
            st.warning(result["error"])
        elif result["rows"] is not None:
            st.dataframe(
                pd.DataFrame(result["rows"], columns=result["columns"]),
                use_container_width=True, hide_index=True,
            )
            st.caption(f"Returned {len(result['rows'])} rows (read-only).")
            st.subheader("Bonus: Automatic Result Validation")
            if result["validation"] is True:
                st.success("Correct — result matches the trusted reference.")
            elif result["validation"] is False:
                st.error("Incorrect — result differs from the trusted reference.")
            else:
                st.info("Validation unavailable for edited/custom questions.")
    st.divider()
