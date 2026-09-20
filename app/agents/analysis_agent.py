import time

from app.config.settings import settings
from app.guardrails.output_guardrails import validate_analysis_output
from app.models.analysis import AnalysisResult
from app.models.article import Article
from app.services.llm_gateway import llm_gateway


class AnalysisAgent:
    """
    Converts a relevant marketing article into
    executive-ready business intelligence.
    """

    SYSTEM_PROMPT = """
You are an executive marketing intelligence analyst.

Analyze the supplied marketing news article and produce
concise, evidence-based business intelligence.

Your output must contain:

1. Headline
2. Summary
3. Why It Matters
4. Recommended Action
5. Supporting Points

SUMMARY:
Write 2-3 concise sentences explaining what happened.

WHY IT MATTERS:
Explain why this development matters to a marketing leader.
Focus on business implications such as:
- marketing strategy
- customer acquisition
- customer experience
- marketing technology
- competitive positioning
- operational efficiency
- AI adoption

RECOMMENDED ACTION:
Suggest a practical action a marketing team could consider.

Do not invent facts that are not supported by the article.

Do not exaggerate the impact.

Separate facts from implications.

Keep the output concise and executive-friendly.
"""

    def analyze(self, article: Article) -> AnalysisResult:
        """
        Generate executive-ready intelligence for an article.

        Retries up to MAX_LLM_RETRIES times on transient
        429 / rate-limit errors. All other exceptions are
        re-raised immediately.
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

Article content:
{article.content or "Full article content is not available."}

Analyze this article.

Return ONLY valid JSON.

The JSON MUST use these exact field names:

{{
  "headline": "...",
  "summary": "...",
  "why_it_matters": "...",
  "recommended_action": "...",
  "supporting_points": ["...", "..."]
}}

IMPORTANT:
- Use lowercase field names exactly as shown.
- Use underscores exactly as shown.
- Do NOT use "Headline".
- Do NOT use "Summary".
- Do NOT use "Why It Matters".
- Do NOT use "Recommended Action".
- Do NOT use "Supporting Points".
- Do not return Markdown.
- Do not wrap the JSON in ```json.
- Do not add text outside the JSON.
"""

        structured_llm = llm_gateway.structured(
            AnalysisResult
        )

        last_exception = None

        for attempt in range(
            1,
            settings.MAX_LLM_RETRIES + 1,
        ):

            try:

                result = structured_llm.invoke(prompt)

                return validate_analysis_output(result)

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
                    "[ANALYSIS] "
                    f"Rate limit detected. "
                    f"Retrying in {delay} seconds "
                    f"(attempt {attempt + 1}/"
                    f"{settings.MAX_LLM_RETRIES})"
                )

                time.sleep(delay)

        raise last_exception


analysis_agent = AnalysisAgent()