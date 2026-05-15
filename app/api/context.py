# app/api/context.py

from fastapi import APIRouter

from app.project_context.context_builder import build_project_context
from app.project_context.repository_registry import (
    resolve_repository_path
)

router = APIRouter()


@router.get("/context/{repository}")
async def get_context(repository: str):

    repo_path = resolve_repository_path(repository)

    if not repo_path:

        return {
            "error": "repository not mapped"
        }

    context = build_project_context(
        repo_path=repo_path,
        repository=repository
    )

    return context