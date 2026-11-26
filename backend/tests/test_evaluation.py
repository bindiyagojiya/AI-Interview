import pytest
from app.services.evaluation_service import evaluation_service

def test_evaluation_empty_answer():
    result = evaluation_service.evaluate(
        candidate_answer="",
        reference_answer="List comprehensions provide a concise way to create lists.",
        key_concepts=["concise", "iterable", "list"]
    )
    assert result.overall_score == 0.0
    assert result.tfidf_score == 0.0
    assert len(result.missing_concepts) == 3

def test_evaluation_short_answer():
    result = evaluation_service.evaluate(
        candidate_answer="It is good.",
        reference_answer="List comprehensions provide a concise way to create lists.",
        key_concepts=["concise", "iterable", "list"]
    )
    assert result.overall_score <= 15.0
    assert "brief" in result.feedback_improvements.lower()

def test_evaluation_high_quality_answer():
    reference = "List comprehensions provide a concise and readable syntax for creating new lists from existing iterables with high performance."
    candidate = "A list comprehension gives a concise and readable syntax to construct lists from an existing iterable, offering clean syntax and performance."
    concepts = ["concise syntax", "iterable", "performance", "readability"]

    result = evaluation_service.evaluate(
        candidate_answer=candidate,
        reference_answer=reference,
        key_concepts=concepts
    )

    assert result.overall_score >= 60.0
    assert result.tfidf_score > 30.0
    assert result.relevance_score >= 55.0
    assert result.correctness_score >= 50.0
    assert len(result.missing_concepts) < len(concepts)

def test_evaluation_score_bounds():
    result = evaluation_service.evaluate(
        candidate_answer="Test text with arbitrary words to ensure score boundaries remain safe.",
        reference_answer="Reference text containing benchmark concepts.",
        key_concepts=["benchmark", "concepts"]
    )

    for score in [
        result.overall_score,
        result.tfidf_score,
        result.semantic_score,
        result.correctness_score,
        result.relevance_score,
        result.completeness_score,
        result.clarity_score
    ]:
        assert 0.0 <= score <= 100.0
