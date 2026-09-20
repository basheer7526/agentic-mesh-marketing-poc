"""
Workflow service.

Encapsulates all business logic for running and retrieving
marketing intelligence workflows.

FastAPI routes call only this module — no graph or agent
imports belong in route handlers.

In-memory store is clearly isolated behind module-level
state so it can be replaced with a database later without
touching the API layer.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from app.models.workflow import (
    DigestItemResponse,
    DigestResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)
from app.orchestration.graph import marketing_graph


# ---------------------------------------------------------------------------
# IN-MEMORY STORE
# Deliberately isolated here so the storage backend can be
# swapped (Redis, Postgres, etc.) without changing routes.
# ---------------------------------------------------------------------------

_workflow_store: Dict[str, WorkflowRunResponse] = {}


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def run_workflow(
    request: WorkflowRunRequest,
) -> WorkflowRunResponse:
    """
    Run the full marketing intelligence workflow.

    1. Generates a unique workflow_id.
    2. Constructs the initial LangGraph state.
    3. Invokes marketing_graph.
    4. Transforms the raw state into WorkflowRunResponse.
    5. Stores the response in the in-memory store.

    Returns the WorkflowRunResponse.
    """

    workflow_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)

    initial_state = {
        "task": request.task,
        "workflow_id": workflow_id,
        "articles": [],
        "unique_articles": [],
        "research_results": [],
        "relevance_results": [],
        "relevant_articles": [],
        "analysis_results": [],
        "rag_context": [],
        "priority_results": [],
        "digest": {},
        "errors": [],
        "max_evaluations": request.max_evaluations,
        "execution_metadata": {
            "max_articles": request.max_articles,
            "workflow_id": workflow_id,
        },
    }

    try:

        final_state = marketing_graph.invoke(initial_state)

        completed_at = datetime.now(timezone.utc)

        response = _build_response(
            workflow_id=workflow_id,
            started_at=started_at,
            completed_at=completed_at,
            state=final_state,
            status="completed",
        )

    except Exception as exc:

        completed_at = datetime.now(timezone.utc)

        response = WorkflowRunResponse(
            workflow_id=workflow_id,
            status="failed",
            started_at=started_at,
            completed_at=completed_at,
            errors=[
                {
                    "agent": "workflow_service",
                    "step": "graph_invocation",
                    "error": str(exc),
                }
            ],
        )

    _workflow_store[workflow_id] = response

    return response


def get_workflow(
    workflow_id: str,
) -> Optional[WorkflowRunResponse]:
    """
    Retrieve a previously completed workflow result.

    Returns None if the workflow_id is not found.
    """

    return _workflow_store.get(workflow_id)


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _build_response(
    workflow_id: str,
    started_at: datetime,
    completed_at: datetime,
    state: dict,
    status: str,
) -> WorkflowRunResponse:
    """
    Transform a raw LangGraph final state into a clean
    WorkflowRunResponse without exposing internal state keys.
    """

    digest_response = _build_digest_response(
        state.get("digest")
    )

    return WorkflowRunResponse(
        workflow_id=workflow_id,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        articles_collected=len(
            state.get("articles", [])
        ),
        unique_articles=len(
            state.get("unique_articles", [])
        ),
        relevant_articles=len(
            state.get("relevant_articles", [])
        ),
        analyses_completed=len(
            state.get("analysis_results", [])
        ),
        digest=digest_response,
        errors=state.get("errors", []),
    )


def _build_digest_response(
    digest_data: Optional[dict],
) -> Optional[DigestResponse]:
    """
    Convert the digest dict from LangGraph state into a
    clean DigestResponse, or return None if no digest exists.
    """

    if not digest_data or not digest_data.get("items"):
        return None

    items = [
        DigestItemResponse(
            headline=item.get("headline", ""),
            summary=item.get("summary", ""),
            why_it_matters=item.get("why_it_matters", ""),
            recommended_action=item.get(
                "recommended_action", ""
            ),
            priority=item.get("priority", "Low"),
            source=item.get("source", ""),
            url=item.get("url", ""),
        )
        for item in digest_data.get("items", [])
    ]

    return DigestResponse(
        date=digest_data.get("date", ""),
        total_articles=digest_data.get("total_articles", 0),
        high_priority=digest_data.get("high_priority", 0),
        medium_priority=digest_data.get("medium_priority", 0),
        low_priority=digest_data.get("low_priority", 0),
        items=items,
    )
