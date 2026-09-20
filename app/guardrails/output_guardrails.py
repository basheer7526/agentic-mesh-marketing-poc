from app.models.analysis import (
    AnalysisResult,
    RelevanceResult,
    RAGResult,
)

class GuardrailValidationError(Exception):
    """Raised when an agent output fails validation."""


def validate_relevance_output(
    result: RelevanceResult,
) -> RelevanceResult:

    if not 0.0 <= result.score <= 1.0:
        raise GuardrailValidationError(
            f"Invalid relevance score: {result.score}"
        )

    if result.relevant and result.category is None:
        raise GuardrailValidationError(
            "Relevant article must have a category."
        )

    if not result.reason.strip():
        raise GuardrailValidationError(
            "Relevance reason cannot be empty."
        )

    if not result.relevant and result.category is not None:
        raise GuardrailValidationError(
            "Irrelevant article should not have a category."
        )

    if result.relevant and result.score < 0.5:
        raise GuardrailValidationError(
            "Relevant article should have a score >= 0.5."
        )

    if not result.relevant and result.score >= 0.5:
        raise GuardrailValidationError(
            "Irrelevant article should have a score < 0.5."
        )

    return result


def validate_analysis_output(
    result: AnalysisResult,
) -> AnalysisResult:

    if not result.headline.strip():
        raise GuardrailValidationError(
            "Analysis headline cannot be empty."
        )

    if not result.summary.strip():
        raise GuardrailValidationError(
            "Analysis summary cannot be empty."
        )

    if not result.why_it_matters.strip():
        raise GuardrailValidationError(
            "Why It Matters cannot be empty."
        )

    if not result.recommended_action.strip():
        raise GuardrailValidationError(
            "Recommended Action cannot be empty."
        )

    if not result.supporting_points:
        raise GuardrailValidationError(
            "Analysis must contain at least one supporting point."
        )

    for point in result.supporting_points:
        if not point.strip():
            raise GuardrailValidationError(
                "Supporting points cannot contain empty values."
            )

    return result

def validate_rag_output(
    result: RAGResult,
    retrieved_sources: list[str],
) -> RAGResult:
    """
    Validate RAG output against the context
    actually retrieved from the knowledge base.
    """

    if not result.insight.strip():
        raise GuardrailValidationError(
            "RAG insight cannot be empty."
        )

    if result.context_used and not retrieved_sources:
        raise GuardrailValidationError(
            "RAG cannot claim context was used "
            "when no context was retrieved."
        )

    if not result.context_used and result.supporting_sources:
        raise GuardrailValidationError(
            "Supporting sources cannot exist when "
            "context_used is False."
        )

    allowed_sources = set(retrieved_sources)

    for source in result.supporting_sources:

        if source not in allowed_sources:
            raise GuardrailValidationError(
                f"RAG cited source not present in "
                f"retrieved context: {source}"
            )

    return result