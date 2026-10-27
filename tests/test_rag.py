"""Unit tests: no Gemini key or online database required."""
from decimal import Decimal
import pytest

from rag.knowledge import documents, EXAMPLES
from rag.generator import build_prompt, clean_sql
from rag.validation import compare_results, validate_against_reference


def test_knowledge_contains_10_docs():
    assert len(documents()) == 10


def test_contains_five_sql_examples():
    examples = [row for row in documents() if row[2]["type"] == "few_shot_example"]
    assert len(examples) == 5


def test_generation_requires_retrieval():
    with pytest.raises(ValueError):
        build_prompt("Show sales", [])


def test_prompt_includes_retrieved_knowledge():
    prompt = build_prompt(
        "Show restaurants", [{"id": "schema", "text": "unique retrieved marker"}]
    )
    assert "unique retrieved marker" in prompt
    assert "Show restaurants" in prompt


def test_clean_sql_code_fences():
    assert clean_sql("```sql\nSELECT 1;\n```") == "SELECT 1;"


def test_result_equivalence_with_decimal_values():
    assert compare_results(["price"], [(Decimal("12.00"),)], ["price"], [(12,)])
    assert not compare_results(["price"], [(13,)], ["price"], [(12,)])


def test_reference_is_executed_through_supplied_runner():
    calls = []
    def run(sql):
        calls.append(sql)
        return ["restaurant_id"], [(1,)]
    assert validate_against_reference(3, ["restaurant_id"], [(1,)], run)
    assert calls == [EXAMPLES[3][2]]


def test_unknown_question_has_no_validation():
    assert validate_against_reference(999, [], [], lambda _: None) is None
