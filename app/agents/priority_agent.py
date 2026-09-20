import time

from app.config.settings import settings
from app.models.analysis import AnalysisResult
from app.models.digest import Priority, PriorityResult
from app.services.llm_gateway import llm_gateway


class PriorityAgent:
    """
    Assigns business priority to marketing intelligence.
    """

    SYSTEM_PROMPT = """
You are a Marketing Intelligence Priority Agent.

Your task is to assign a priority level to a marketing
intelligence item.

Allowed priorities:

- High
- Medium
- Low

HIGH:
Use when the development has significant and immediate
business implications.

Examples:
- Major AI or Martech platform changes
- Significant competitor launches
- Major changes affecting customer acquisition
- Important regulatory developments
- Developments that could materially affect marketing strategy

MEDIUM:
Use when the development has meaningful business relevance
but does not require immediate action.

Examples:
- Emerging marketing technology trends
- Notable campaign strategies
- Industry developments
- Moderate customer experience changes

LOW:
Use when the development is useful for awareness but has
limited immediate strategic impact.

Examples:
- Minor marketing developments
- General industry commentary
- Limited-impact announcements

Base the priority on the actual information provided.

Do not assign High priority merely because an article
mentions AI.

Do not invent facts.

Return only the priority level.
"""

    def assign_priority(
        self,
        analysis: AnalysisResult,
    ) -> PriorityResult:
        """
        Assign a business priority to an analysis result.

        Retries up to MAX_LLM_RETRIES times on transient
        429 / rate-limit errors. All other exceptions are
        re-raised immediately.
        """

        prompt = f"""
{self.SYSTEM_PROMPT}

ARTICLE INTELLIGENCE

Headline:
{analysis.headline}

Summary:
{analysis.summary}

Why It Matters:
{analysis.why_it_matters}

Recommended Action:
{analysis.recommended_action}

Supporting Points:
{analysis.supporting_points}

Return the priority as JSON.

The JSON must contain exactly this field:

{{
  "priority": "High"
}}

The value must be exactly one of:

- High
- Medium
- Low

Do not return Markdown.
Do not add explanatory text outside the JSON.
"""

        structured_llm = llm_gateway.structured(
            PriorityResult
        )

        last_exception = None

        for attempt in range(
            1,
            settings.MAX_LLM_RETRIES + 1,
        ):

            try:

                return structured_llm.invoke(prompt)

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
                    "[PRIORITY] "
                    f"Rate limit detected. "
                    f"Retrying in {delay} seconds "
                    f"(attempt {attempt + 1}/"
                    f"{settings.MAX_LLM_RETRIES})"
                )

                time.sleep(delay)

        raise last_exception


priority_agent = PriorityAgent()