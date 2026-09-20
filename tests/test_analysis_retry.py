"""
Unit tests for AnalysisAgent retry/backoff behavior.

Uses unittest.mock to inject controlled failures without
making real LLM calls. Verifies:

1. Successful call returns AnalysisResult.
2. 429 error triggers a retry and succeeds on next attempt.
3. Non-429 error is re-raised immediately (no retry).
4. Exhausted retries re-raise the last 429 exception.
"""

import unittest
from unittest.mock import MagicMock, patch

from app.agents.analysis_agent import AnalysisAgent
from app.models.analysis import AnalysisResult
from app.models.article import Article


def _make_article() -> Article:
    return Article(
        title="AI marketing platform improves ROI",
        url="https://example.com/ai-marketing",
        source="Test Source",
        description="A new AI marketing platform launched.",
    )


def _make_analysis_result() -> AnalysisResult:
    return AnalysisResult(
        headline="AI Platform Boosts Marketing ROI",
        summary=(
            "A new AI marketing platform has launched, "
            "offering improved campaign personalization and ROI."
        ),
        why_it_matters=(
            "Marketing teams can reduce manual effort "
            "and improve campaign performance."
        ),
        recommended_action=(
            "Evaluate the platform for a pilot campaign."
        ),
        supporting_points=[
            "Reduces campaign setup time by 40%.",
            "AI-driven personalization improves CTR.",
        ],
    )


class TestAnalysisAgentRetry(unittest.TestCase):

    def setUp(self):
        self.agent = AnalysisAgent()
        self.article = _make_article()
        self.expected_result = _make_analysis_result()

    @patch(
        "app.agents.analysis_agent.llm_gateway"
    )
    @patch(
        "app.agents.analysis_agent.validate_analysis_output"
    )
    def test_successful_call_returns_result(
        self,
        mock_validate,
        mock_gateway,
    ):
        """First attempt succeeds — returns AnalysisResult."""

        mock_structured = MagicMock()
        mock_gateway.structured.return_value = mock_structured
        mock_structured.invoke.return_value = (
            self.expected_result
        )
        mock_validate.return_value = self.expected_result

        result = self.agent.analyze(self.article)

        self.assertEqual(result, self.expected_result)
        self.assertEqual(
            mock_structured.invoke.call_count, 1
        )

    @patch("app.agents.analysis_agent.time.sleep")
    @patch(
        "app.agents.analysis_agent.llm_gateway"
    )
    @patch(
        "app.agents.analysis_agent.validate_analysis_output"
    )
    def test_429_triggers_retry_and_succeeds(
        self,
        mock_validate,
        mock_gateway,
        mock_sleep,
    ):
        """429 on first attempt → retry → succeeds."""

        mock_structured = MagicMock()
        mock_gateway.structured.return_value = mock_structured

        rate_limit_exc = Exception(
            "Error code: 429 - rate_limit_exceeded"
        )

        mock_structured.invoke.side_effect = [
            rate_limit_exc,
            self.expected_result,
        ]
        mock_validate.return_value = self.expected_result

        result = self.agent.analyze(self.article)

        self.assertEqual(result, self.expected_result)
        self.assertEqual(
            mock_structured.invoke.call_count, 2
        )
        mock_sleep.assert_called_once()

    @patch("app.agents.analysis_agent.time.sleep")
    @patch(
        "app.agents.analysis_agent.llm_gateway"
    )
    def test_non_429_error_raises_immediately(
        self,
        mock_gateway,
        mock_sleep,
    ):
        """Non-transient error is re-raised — no retry."""

        mock_structured = MagicMock()
        mock_gateway.structured.return_value = mock_structured

        auth_error = Exception(
            "401 Unauthorized: invalid API key"
        )
        mock_structured.invoke.side_effect = auth_error

        with self.assertRaises(Exception) as ctx:
            self.agent.analyze(self.article)

        self.assertIn("401", str(ctx.exception))
        # Must not retry a non-transient error
        self.assertEqual(
            mock_structured.invoke.call_count, 1
        )
        mock_sleep.assert_not_called()

    @patch("app.agents.analysis_agent.time.sleep")
    @patch(
        "app.agents.analysis_agent.llm_gateway"
    )
    def test_exhausted_retries_reraises(
        self,
        mock_gateway,
        mock_sleep,
    ):
        """All retries exhausted → last 429 is re-raised."""

        mock_structured = MagicMock()
        mock_gateway.structured.return_value = mock_structured

        rate_limit_exc = Exception(
            "Error code: 429 - rate_limit_exceeded"
        )
        mock_structured.invoke.side_effect = rate_limit_exc

        with self.assertRaises(Exception) as ctx:
            self.agent.analyze(self.article)

        self.assertIn("429", str(ctx.exception))
        # Should have attempted MAX_LLM_RETRIES times
        from app.config.settings import settings
        self.assertEqual(
            mock_structured.invoke.call_count,
            settings.MAX_LLM_RETRIES,
        )


def main():
    print("\n===== ANALYSIS RETRY UNIT TESTS =====\n")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(
        TestAnalysisAgentRetry
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
