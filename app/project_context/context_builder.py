# app/project_context/context_builder.py

from app.project_context.scanner import scan_repository
from app.project_context.stack_detector import detect_stack
from app.project_context.service_discovery import discover_services
from app.project_context.models import ProjectContext, ServiceContext


def build_project_context(repo_path: str, repository: str):

    # discover services in the repository (monorepo-aware)
    services = discover_services(repo_path)

    enriched_services = []

    for service in services:

        files = scan_repository(service.path)

        # detect_stack returns a dict with service-level info
        detected = detect_stack(files, service.name)

        # enrich the ServiceContext
        enriched = service.model_copy(update=detected)

        enriched_services.append(enriched)

    project = ProjectContext(
        repository=repository,
        services=enriched_services
    )

    # also keep legacy top-level fields based on repository root for compatibility
    root_files = scan_repository(repo_path)
    root_detected = detect_stack(root_files, repository)

    for k, v in root_detected.items():
        # only set top-level legacy fields that exist on ProjectContext
        if hasattr(project, k):
            setattr(project, k, v)

    return project
