from app.models.article import Article
from app.models.analysis import RelevanceResult
from app.services.llm_gateway import llm_gateway
from app.guardrails.output_guardrails import (
    validate_relevance_output,
)

import time

from app.config.settings import settings


class RelevanceAgent:
    """
    Determines whether a marketing article is relevant
    to the Marketing News Intelligence workflow.

    The agent uses GPT-OSS 20B through the LLM Gateway
    and returns a validated RelevanceResult.
    """

    SYSTEM_PROMPT = """
You are a Marketing Intelligence Relevance Agent.

Determine whether the supplied article is relevant to
marketing leadership intelligence.

The only allowed categories are:

1. AI in Marketing
2. Demand Generation
3. Customer Experience
4. Martech
5. Competitor Activity

Classification rules:

AI in Marketing:
- AI in advertising
- Generative AI for marketing
- AI-powered content
- AI personalization
- AI campaign optimization
- AI marketing platforms

Demand Generation:
- Lead generation
- Customer acquisition
- Pipeline generation
- Conversion
- B2B demand generation
- Marketing funnel performance

Customer Experience:
- Personalization
- Customer journeys
- Customer engagement
- Retention
- Loyalty
- Customer experience technology

Martech:
- CRM
- CDP
- Marketing automation
- Marketing analytics
- Advertising technology
- Marketing software and platforms

Competitor Activity:
- Competitor product launches
- Competitor campaigns
- Strategic partnerships
- Acquisitions
- Major competitive developments

Do not classify an article as relevant simply because
it contains the word "marketing" or "AI".

Only classify it as relevant when there is a meaningful
connection to one of the five categories.

The relevance score must be between 0 and 1.
"""

    def analyze(self, article: Article) -> RelevanceResult:
        """
        Analyze one article and return structured relevance output.
        """

        prompt = f"""
{self.SYSTEM_PROMPT}

ARTICLE

Source:
{article.source}

Title:
{article.title}

Description:
{article.description or "No description available"}

Determine whether this article is relevant.

Return the result as JSON.

The JSON MUST contain all four fields:
- relevant
- category
- score
- reason

If the article is irrelevant:
- relevant must be false
- category must be null
- score should normally be between 0 and 0.49
- reason must explain briefly why the article is not relevant

If the article is relevant:
- relevant must be true
- category must contain exactly one allowed category
- score should normally be between 0.5 and 1.0
- reason must explain why the article belongs to that category

Do not omit any field.
Do not return Markdown.
Do not return explanatory text outside the JSON.
"""

        structured_llm = llm_gateway.structured(
            RelevanceResult
        )

        last_exception = None

        for attempt in range(
            1,
            settings.MAX_LLM_RETRIES + 1,
        ):

            try:

                result = structured_llm.invoke(
                    prompt
                )

                return validate_relevance_output(
                    result
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
                    "[RELEVANCE] "
                    f"Rate limit detected. "
                    f"Retrying in {delay} seconds "
                    f"(attempt {attempt + 1}/"
                    f"{settings.MAX_LLM_RETRIES})"
                )

                time.sleep(delay)

        raise last_exception


# Shared agent instance used by the application.
relevance_agent = RelevanceAgent()