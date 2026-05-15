# app/project_context/service_discovery.py

from pathlib import Path
from app.project_context.models import ServiceContext


def discover_services(repo_path: str):

    services = []

    base = Path(repo_path)

    if not base.exists():
        return services

    for path in base.iterdir():

        if not path.is_dir():
            continue

        # heurística monorepo: detect build files in service root
        if (path / "pom.xml").exists() or (path / "build.gradle").exists() or (path / "package.json").exists():

            services.append(ServiceContext(
                name=path.name,
                path=str(path)
            ))

    return services

