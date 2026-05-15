# app/project_context/context_registry.py

from pathlib import Path

PROJECTS = {
    "agentic-ms-user": "/home/mhj/git/agentic-ms-user",
    "agentic-ms-order": "/home/mhj/git/agentic-ms-order",
    # Local mapping for this monorepo so codegen can operate on the workspace
    "devflow-ai": "/home/mhj/git/devflow-ai"
}


def get_project_path(repository_or_service: str):
    """
    Resolve a project path by repository name or service name.

    Strategy:
    - Check explicit PROJEC TS mapping
    - If not found, try to resolve to monorepo/services/{name} or monorepo/services/{name}-service
    - Return None if not found
    """

    if not repository_or_service:
        return None

    # 1) explicit mapping
    path = PROJECTS.get(repository_or_service)
    if path:
        return path

    # 2) try to resolve under monorepo services/ or directly under repo root
    try:
        base = Path(__file__).resolve().parents[3]  # devflow-ai

        # check top-level directory matching the service name
        candidate_root = base / repository_or_service
        if candidate_root.exists():
            return str(candidate_root)

        # check under services/ directory
        candidate = base / "services" / repository_or_service
        if candidate.exists():
            return str(candidate)

        # try with -service suffix under root and services/
        candidate_root2 = base / f"{repository_or_service}-service"
        if candidate_root2.exists():
            return str(candidate_root2)

        candidate2 = base / "services" / f"{repository_or_service}-service"
        if candidate2.exists():
            return str(candidate2)

    except Exception:
        pass

    return None
