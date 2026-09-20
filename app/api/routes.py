"""
FastAPI route handlers for the Marketing Intelligence API.

Routes delegate all business logic to workflow_service.
No agent, graph, or model imports belong here.

Prefix: /api/v1  (applied in app/main.py)
"""

from fastapi import APIRouter, HTTPException

from app.models.workflow import (
    HealthResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)
from app.services import workflow_service

router = APIRouter()


# ---------------------------------------------------------------------------
# HEALTH
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["Health"],
)
def health() -> HealthResponse:
    """
    Returns 200 with status 'healthy' when the service is up.
    """

    return HealthResponse(status="healthy")


# ---------------------------------------------------------------------------
# WORKFLOW — RUN
# ---------------------------------------------------------------------------

@router.post(
    "/workflows/run",
    response_model=WorkflowRunResponse,
    summary="Run the marketing intelligence workflow",
    tags=["Workflows"],
)
def run_workflow(
    request: WorkflowRunRequest,
) -> WorkflowRunResponse:
    """
    Trigger the full marketing intelligence pipeline:

    Research → Deduplication → Relevance → Analysis
    → RAG → Priority → Digest → Notification

    Returns a structured digest of the top relevant articles
    with business intelligence, RAG context, and priority scores.

    **max_articles** controls how many relevant articles are
    passed through the expensive Analysis / RAG / Priority stages.
    """

    return workflow_service.run_workflow(request)


# ---------------------------------------------------------------------------
# WORKFLOW — GET BY ID
# ---------------------------------------------------------------------------

@router.get(
    "/workflows/{workflow_id}",
    response_model=WorkflowRunResponse,
    summary="Retrieve a workflow result by ID",
    tags=["Workflows"],
)
def get_workflow(
    workflow_id: str,
) -> WorkflowRunResponse:
    """
    Retrieve a previously completed workflow result.

    Results are stored in an in-memory cache for the lifetime
    of the server process.

    Returns 404 if the workflow_id is not found.
    """

    result = workflow_service.get_workflow(workflow_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_id}' not found.",
        )

    return result
