# app/project_context/scanner.py

from pathlib import Path


def scan_repository(repo_path: str):

    files = []

    for path in Path(repo_path).rglob("*"):

        if path.is_file():

            files.append(str(path))

    return files