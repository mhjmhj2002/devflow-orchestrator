# app/project_context/models.py

from pydantic import BaseModel
from typing import List, Optional


class ServiceContext(BaseModel):
    name: str
    path: str

    language: Optional[str] = None
    framework: Optional[str] = None
    build_tool: Optional[str] = None

    java_version: Optional[str] = None

    dependencies: List[str] = []
    entrypoints: List[str] = []


class ProjectContext(BaseModel):
    repository: str

    # List of discovered services inside the repository (monorepo aware)
    services: List[ServiceContext] = []

    # legacy/top-level fields (kept for backward compatibility)
    language: Optional[str] = None
    framework: Optional[str] = None
    build_tool: Optional[str] = None

    java_version: Optional[str] = None

    dependencies: List[str] = []

    architecture_hints: List[str] = []

    source_directories: List[str] = []