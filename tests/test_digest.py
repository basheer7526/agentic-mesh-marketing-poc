"""
Unit tests for the digest_node (pure Python — no LLM call).

Verifies:
1. DigestItem is assembled correctly from analysis + priority + article.
2. DailyDigest counts are correct.
3. Priority enum values are stored correctly.
4. Empty priority_results produces an empty digest.
5. digest_node output is a plain dict (not a Pydantic object).
"""

import unittest
from datetime import datetime, timezone

from app.models.digest import DailyDigest, DigestItem, Priority
from app.orchestration.graph import digest_node


def _make_state(priority_results: list) -> dict:
    return {
        "priority_results": priority_results,
        "errors": [],
        "execution_metadata": {},
    }


def _make_priority_result(
    headline: str,
    priority: str,
    source: str = "Test Source",
    url: str = "https://example.com/test",
) -> dict:
    return {
        "article": {
            "title": headline,
            "url": url,
            "source": source,
        },
        "analysis": {
            "headline": headline,
            "summary": (
                "This is a test summary with enough "
                "length to pass validation rules."
            ),
            "why_it_matters": "It matters for marketing.",
            "recommended_action": "Take action now.",
            "supporting_points": ["Point 1", "Point 2"],
        },
        "priority": {
            "priority": priority,
        },
    }


class TestDigestNode(unittest.TestCase):

    def test_empty_priority_results_produces_empty_digest(self):
        """No priority results → digest with zero items."""

        state = _make_state([])
        result = digest_node(state)

        digest = result["digest"]
        self.assertIsInstance(digest, dict)
        self.assertEqual(digest["total_articles"], 0)
        self.assertEqual(digest["high_priority"], 0)
        self.assertEqual(digest["medium_priority"], 0)
        self.assertEqual(digest["low_priority"], 0)
        self.assertEqual(len(digest["items"]), 0)

    def test_single_high_priority_item(self):
        """One High item → correct digest counts."""

        state = _make_state([
            _make_priority_result(
                "Major AI Launch", "High"
            )
        ])
        result = digest_node(state)

        digest = result["digest"]
        self.assertEqual(digest["total_articles"], 1)
        self.assertEqual(digest["high_priority"], 1)
        self.assertEqual(digest["medium_priority"], 0)
        self.assertEqual(digest["low_priority"], 0)
        self.assertEqual(
            digest["items"][0]["priority"], "High"
        )

    def test_mixed_priorities_counted_correctly(self):
        """Multiple items with different priorities."""

        state = _make_state([
            _make_priority_result("Article A", "High"),
            _make_priority_result("Article B", "High"),
            _make_priority_result("Article C", "Medium"),
            _make_priority_result("Article D", "Low"),
            _make_priority_result("Article E", "Low"),
        ])
        result = digest_node(state)

        digest = result["digest"]
        self.assertEqual(digest["total_articles"], 5)
        self.assertEqual(digest["high_priority"], 2)
        self.assertEqual(digest["medium_priority"], 1)
        self.assertEqual(digest["low_priority"], 2)

    def test_digest_stored_as_plain_dict(self):
        """digest must be a dict, not a Pydantic object."""

        state = _make_state([
            _make_priority_result("Test Article", "Medium")
        ])
        result = digest_node(state)

        self.assertIsInstance(result["digest"], dict)

    def test_digest_item_fields_populated(self):
        """DigestItem fields match source data."""

        state = _make_state([
            _make_priority_result(
                headline="AI Martech Revolution",
                priority="High",
                source="MarTech Weekly",
                url="https://martech.example.com/ai",
            )
        ])
        result = digest_node(state)

        item = result["digest"]["items"][0]
        self.assertEqual(item["headline"], "AI Martech Revolution")
        self.assertEqual(item["source"], "MarTech Weekly")
        self.assertEqual(item["url"], "https://martech.example.com/ai")
        self.assertEqual(item["priority"], "High")
        self.assertIn("summary", item)
        self.assertIn("why_it_matters", item)
        self.assertIn("recommended_action", item)

    def test_digest_date_is_set(self):
        """Digest date is populated (YYYY-MM-DD format)."""

        state = _make_state([])
        result = digest_node(state)

        date_str = result["digest"]["date"]
        # Verify it parses as a valid date
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        self.assertIsInstance(parsed, datetime)

    def test_no_errors_on_valid_input(self):
        """Valid input produces no errors in state."""

        state = _make_state([
            _make_priority_result("Clean Article", "Low")
        ])
        result = digest_node(state)

        self.assertEqual(result["errors"], [])


def main():
    print("\n===== DIGEST NODE UNIT TESTS =====\n")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDigestNode)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
