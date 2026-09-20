import time

from app.config.settings import settings
from app.guardrails.output_guardrails import validate_rag_output
from app.models.analysis import AnalysisResult, RAGResult
from app.services.llm_gateway import llm_gateway
from app.tools.rag_tool import rag_tool


class RAGAgent:
    """
    Connects marketing news intelligence with
    organization-specific business context.
    """

    SYSTEM_PROMPT = """
You are a Marketing Intelligence RAG Agent.

Your job is to connect a marketing news development
with relevant business context retrieved from the
organization's knowledge base.

IMPORTANT:

Use only the supplied retrieved context when making
organization-specific claims.

Do not invent company priorities or business facts.

If the retrieved context does not provide useful
information, clearly indicate that context was not
sufficient.

Focus on:

- strategic relevance
- customer acquisition
- customer experience
- AI adoption
- Martech
- marketing efficiency
- competitive implications

The retrieved knowledge is supporting context.
It must not override facts from the original article.

Return concise executive-level intelligence.
"""

    def analyze(
        self,
        analysis: AnalysisResult,
    ) -> RAGResult:

        # --------------------------------------------------
        # 1. Build semantic retrieval query
        # --------------------------------------------------

        query = f"""
{analysis.headline}

{analysis.summary}

{analysis.why_it_matters}

{analysis.recommended_action}
"""

        # --------------------------------------------------
        # 2. Retrieve relevant business context
        # --------------------------------------------------

        retrieved_context = rag_tool.retrieve(
            query=query,
            top_k=3,
        )

        # --------------------------------------------------
        # 3. Handle case where no context is retrieved
        #    (fast path — no LLM call, no retry needed)
        # --------------------------------------------------

        if not retrieved_context:
            return RAGResult(
                insight=(
                    "No relevant organizational context "
                    "was retrieved for this development."
                ),
                supporting_sources=[],
                context_used=False,
            )

        # --------------------------------------------------
        # 4. Prepare retrieved context for the LLM
        # --------------------------------------------------

        context_text = "\n\n".join(
            [
                f"SOURCE: {item['source']}\n"
                f"{item['content']}"
                for item in retrieved_context
            ]
        )

        # --------------------------------------------------
        # 5. Build RAG reasoning prompt
        # --------------------------------------------------

        prompt = f"""
{self.SYSTEM_PROMPT}

NEWS INTELLIGENCE

Headline:
{analysis.headline}

Summary:
{analysis.summary}

Why It Matters:
{analysis.why_it_matters}

Recommended Action:
{analysis.recommended_action}

RETRIEVED BUSINESS CONTEXT

{context_text}

Analyze how the news development relates to the
retrieved business context.

Return ONLY valid JSON.

Use exactly these fields:

{{
  "insight": "...",
  "supporting_sources": ["...", "..."],
  "context_used": true
}}

Rules:

- insight must be concise.
- supporting_sources must contain the filenames
  of the retrieved context used.
- context_used must be true when the retrieved
  context provides meaningful information.
- Do not invent sources.
- Do not return Markdown.
- Do not add text outside the JSON.
"""

        # --------------------------------------------------
        # 6. Generate structured RAG response with retry
        #    Only the actual LLM call is retried.
        # --------------------------------------------------

        structured_llm = llm_gateway.structured(RAGResult)

        retrieved_sources = [
            item["source"]
            for item in retrieved_context
        ]

        last_exception = None

        for attempt in range(
            1,
            settings.MAX_LLM_RETRIES + 1,
        ):

            try:

                result = structured_llm.invoke(prompt)

                return validate_rag_output(
                    result,
                    retrieved_sources,
                )

            except Exception as exc:

                last_exception = exc

                error_text = str(exc).lower()

                is_rate_limit = (
                    "429" in error_text
                    or "rate_limit" in error_text
                    or "rate limit" in error_text
                    or "rate_limit_exceeded" in error_text
                    or "json_validate_failed" in error_text
                    or "failed_generation" in error_text
                )

                if not is_rate_limit:
                    raise

                if attempt >= settings.MAX_LLM_RETRIES:
                    break

                delay = (
                    settings.LLM_RETRY_BASE_DELAY
                    * (2 ** (attempt - 1))
                )

                print(
                    "[RAG] "
                    f"Rate limit detected. "
                    f"Retrying in {delay} seconds "
                    f"(attempt {attempt + 1}/"
                    f"{settings.MAX_LLM_RETRIES})"
                )

                time.sleep(delay)

        raise last_exception


rag_agent = RAGAgent()