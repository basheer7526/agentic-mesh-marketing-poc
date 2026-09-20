"""
FastAPI integration tests using TestClient.

Uses unittest.mock to stub out workflow_service so that
tests do not make real LLM or RSS calls.

Verifies:
1. GET /api/v1/health returns 200 and {"status": "healthy"}.
2. POST /api/v1/workflows/run calls workflow_service.run_workflow.
3. POST /api/v1/workflows/run returns a valid WorkflowRunResponse.
4. GET /api/v1/workflows/{id} returns a result when found.
5. GET /api/v1/workflows/{id} returns 404 when not found.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.workflow import (
    DigestResponse,
    WorkflowRunResponse,
)

client = TestClient(app)


def _make_mock_response(
    workflow_id: str = "test-wf-001",
) -> WorkflowRunResponse:
    return WorkflowRunResponse(
        workflow_id=workflow_id,
        status="completed",
        started_at=datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc),
        completed_at=datetime(
            2026, 9, 19, 12, 5, 0, tzinfo=timezone.utc
        ),
        articles_collected=110,
        unique_articles=110,
        relevant_articles=20,
        analyses_completed=5,
        digest=DigestResponse(
            date="2026-09-19",
            total_articles=5,
            high_priority=2,
            medium_priority=2,
            low_priority=1,
            items=[],
        ),
        errors=[],
    )


class TestHealthEndpoint(unittest.TestCase):

    def test_health_returns_200(self):
        response = client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)

    def test_health_body(self):
        response = client.get("/api/v1/health")
        data = response.json()
        self.assertEqual(data["status"], "healthy")


class TestWorkflowRunEndpoint(unittest.TestCase):

    @patch(
        "app.api.routes.workflow_service.run_workflow"
    )
    def test_run_workflow_returns_200(
        self,
        mock_run,
    ):
        mock_run.return_value = _make_mock_response()

        response = client.post(
            "/api/v1/workflows/run",
            json={
                "task": "Test marketing news task.",
                "max_articles": 5,
            },
        )

        self.assertEqual(response.status_code, 200)

    @patch(
        "app.api.routes.workflow_service.run_workflow"
    )
    def test_run_workflow_response_schema(
        self,
        mock_run,
    ):
        mock_run.return_value = _make_mock_response()

        response = client.post(
            "/api/v1/workflows/run",
            json={
                "task": "Test.",
                "max_articles": 3,
            },
        )

        data = response.json()
        self.assertIn("workflow_id", data)
        self.assertIn("status", data)
        self.assertIn("articles_collected", data)
        self.assertIn("relevant_articles", data)
        self.assertIn("analyses_completed", data)
        self.assertIn("digest", data)
        self.assertIn("errors", data)

    @patch(
        "app.api.routes.workflow_service.run_workflow"
    )
    def test_run_workflow_service_called_with_request(
        self,
        mock_run,
    ):
        """Verify the route passes the request to service."""

        mock_run.return_value = _make_mock_response()

        client.post(
            "/api/v1/workflows/run",
            json={
                "task": "Custom task.",
                "max_articles": 10,
            },
        )

        mock_run.assert_called_once()
        call_arg = mock_run.call_args[0][0]
        self.assertEqual(call_arg.task, "Custom task.")
        self.assertEqual(call_arg.max_articles, 10)

    def test_run_workflow_invalid_max_articles(self):
        """max_articles=0 should fail Pydantic validation."""

        response = client.post(
            "/api/v1/workflows/run",
            json={"max_articles": 0},
        )
        self.assertEqual(response.status_code, 422)

    def test_run_workflow_max_articles_too_large(self):
        """max_articles > 100 should fail validation."""

        response = client.post(
            "/api/v1/workflows/run",
            json={"max_articles": 101},
        )
        self.assertEqual(response.status_code, 422)


class TestWorkflowGetEndpoint(unittest.TestCase):

    @patch(
        "app.api.routes.workflow_service.get_workflow"
    )
    def test_get_existing_workflow_returns_200(
        self,
        mock_get,
    ):
        mock_get.return_value = _make_mock_response(
            "found-wf"
        )

        response = client.get(
            "/api/v1/workflows/found-wf"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["workflow_id"], "found-wf")

    @patch(
        "app.api.routes.workflow_service.get_workflow"
    )
    def test_get_missing_workflow_returns_404(
        self,
        mock_get,
    ):
        mock_get.return_value = None

        response = client.get(
            "/api/v1/workflows/nonexistent-id"
        )

        self.assertEqual(response.status_code, 404)


def main():
    print("\n===== FASTAPI UNIT TESTS =====\n")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(
        loader.loadTestsFromTestCase(TestHealthEndpoint)
    )
    suite.addTests(
        loader.loadTestsFromTestCase(TestWorkflowRunEndpoint)
    )
    suite.addTests(
        loader.loadTestsFromTestCase(TestWorkflowGetEndpoint)
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
