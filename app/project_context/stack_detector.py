# app/project_context/stack_detector.py

from pathlib import Path

from app.project_context.models import ProjectContext


def file_contains(path: str, keyword: str):

    try:
        content = Path(path).read_text()

        return keyword in content

    except Exception:
        return False


def detect_stack(files: list[str], repository: str):

    # Build a lightweight ProjectContext (legacy) and return as dict
    context = ProjectContext(repository=repository)

    # =========================
    # JAVA + MAVEN
    # =========================
    if any("pom.xml" in file for file in files):

        context.language = "Java"
        context.build_tool = "Maven"

    # =========================
    # SPRING BOOT
    # =========================
    for file in files:

        if file.endswith(".java"):

            if file_contains(file, "@SpringBootApplication"):

                context.framework = "Spring Boot"
                break

    # =========================
    # JAVA VERSION
    # =========================
    pom_files = [
        file for file in files
        if file.endswith("pom.xml")
    ]

    for pom in pom_files:

        try:
            content = Path(pom).read_text()

            if "<java.version>21</java.version>" in content:
                context.java_version = "21"

        except Exception:
            pass

    # =========================
    # DEPENDENCIES
    # =========================
    dependency_map = {
        "spring-boot-starter-web": "Spring Web",
        "spring-boot-starter-data-jpa": "Spring Data JPA",
        "postgresql": "PostgreSQL",
        "lombok": "Lombok",
        "springdoc-openapi": "OpenAPI"
    }

    for pom in pom_files:

        try:
            content = Path(pom).read_text()

            for dependency, label in dependency_map.items():

                if dependency in content:
                    context.dependencies.append(label)

        except Exception:
            pass

    # =========================
    # SOURCE DIRS
    # =========================
    src_dirs = [
        file for file in files
        if "/src/main/" in file
    ]

    context.source_directories = src_dirs[:20]

    # Return a dict suitable to update a ServiceContext via model_copy(update=...)
    return {
        "language": context.language,
        "framework": context.framework,
        "build_tool": context.build_tool,
        "java_version": context.java_version,
        "dependencies": context.dependencies,
        "entrypoints": context.source_directories[:10]
    }
