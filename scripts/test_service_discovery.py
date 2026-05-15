#!/usr/bin/env python3
# scripts/test_service_discovery.py

from app.project_context.service_discovery import discover_services

services = discover_services("/home/mhj/git/devflow-ai")

print("\n=== SERVICES ===\n")
for s in services:
    print(s.name, s.path)

