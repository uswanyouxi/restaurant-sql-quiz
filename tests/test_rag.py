"""RAG unit tests requiring no API key or online PostgreSQL connection."""
from decimal import Decimal

from rag.generator import build_prompt, clean_sql, format_sql_for_display
from rag.knowledge import documents, EXAMPLE_QUESTIONS
from rag.validation import compare_results, validate_against_reference


def test_knowledge_contains_schema_and_five_examples():
    docs = documents()
    assert len(docs) >= 8
    assert len([doc for doc in docs if doc[2]["type"] == "few_shot_example"]) == 5


def test_context_must_be_retrieved():
    try:
        build_prompt("Show sales", [])
        assert False, "Empty retrieval must fail"
    except ValueError:
        pass


def test_prompt_uses_retrieved_documents():
    prompt = build_prompt("Show all restaurants", [{"id": "schema", "text": "distinct context marker"}])
    assert "distinct context marker" in prompt
    assert "Show all restaurants" in prompt


def test_strip_markdown_fences():
    assert clean_sql("```sql\nSELECT 1;\n```") == "SELECT 1;"


def test_decimal_result_equivalence():
    assert compare_results(["price"], [(Decimal("12.00"),)], ["price"], [(12,)])
    assert not compare_results(["price"], [(13,)], ["price"], [(12,)])


def test_validation_uses_reference_in_same_readonly_runner():
    captured = []
    def trusted_execute(sql):
        captured.append(sql)
        return ["restaurant_id"], [(1,)]
    assert validate_against_reference(3, ["restaurant_id"], [(1,)], trusted_execute)
    assert captured == [EXAMPLE_QUESTIONS[3][2]]


def test_validation_skips_unknown_question():
    assert validate_against_reference(999, [], [], lambda _: None) is None


def test_display_formatting_does_not_modify_executed_sql():
    original_sql = "SELECT name, city FROM public.restaurants ORDER BY id;"
    pretty = format_sql_for_display(original_sql)
    assert "\\n" in pretty
    assert "FROM public.restaurants" in pretty
    assert original_sql == "SELECT name, city FROM public.restaurants ORDER BY id;"
