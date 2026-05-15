# app/project_context/repository_registry.py

REPOSITORY_MAP = {
    "agentic-ms-user": "/home/mhj/git/agentic-ms-user",
    "agentic-ms-order": "/home/mhj/git/agentic-ms-order"
}


def resolve_repository_path(repository_name: str):

    return REPOSITORY_MAP.get(repository_name)