"""Main architecture generator — orchestrates all sub-generators."""

import os
from pathlib import Path
from datetime import datetime
from typing import Any

from archon.core.llm import LLMClient
from archon.core.diagram import DiagramGenerator
from archon.core.schema import SchemaGenerator
from archon.core.api_spec import APISpecGenerator
from archon.core.infra import InfraGenerator
from archon.core.exporter import RepoExporter


SYSTEM_PROMPT = """You are Archon, an expert system architect. Given a natural language description
of an application, you produce a complete architecture specification as JSON.

Respond with ONLY a JSON object (no markdown, no explanation) matching this structure:
{
  "app_name": "string",
  "description": "string",
  "style": "microservices|monolith|serverless|hybrid",
  "components": [
    {
      "name": "string",
      "type": "service|database|cache|queue|storage|cdn|gateway|function",
      "technology": "string",
      "purpose": "string",
      "ports": ["number"],
      "dependencies": ["component_name"]
    }
  ],
  "database_schema": {
    "tables": [
      {
        "name": "string",
        "columns": [
          {"name": "string", "type": "string", "primary_key": false, "nullable": true, "unique": false}
        ]
      }
    ]
  },
  "api_endpoints": [
    {
      "method": "GET|POST|PUT|PATCH|DELETE",
      "path": "string",
      "summary": "string",
      "request_body": {},
      "response_example": {}
    }
  ],
  "infrastructure": {
    "cloud": "aws|gcp|azure",
    "compute": "ecs|cloudrun|functions|kubernetes",
    "database_service": "rds|cloudsql|cosmosdb|postgres",
    "cache_service": "elasticache|memorystore|redis",
    "cdn": "cloudfront|cloudflare|fastly"
  },
  "environment_variables": [
    {"name": "string", "description": "string", "required": true}
  ]
}"""


class Architect:
    def __init__(self, config: dict[str, Any], display: Any = None):
        self.config = config
        self.display = display
        self.llm = LLMClient(config)
        self.diagram_gen = DiagramGenerator()
        self.schema_gen = SchemaGenerator()
        self.api_gen = APISpecGenerator()
        self.infra_gen = InfraGenerator()
        self.exporter = RepoExporter()

    def generate(
        self,
        description: str,
        style: str | None = None,
        cloud: str = "any",
        output_dir: str = "./archon-output",
        export_repo: bool = False,
    ) -> dict | None:
        if self.display:
            self.display.print_step("Analyzing description...")

        style_hint = f" Prefer a {style} architecture style." if style else ""
        cloud_hint = f" Target cloud provider: {cloud}." if cloud != "any" else ""

        user_prompt = f"""Design a complete system architecture for this application:

{description}
{style_hint}{cloud_hint}

Return ONLY the JSON specification."""

        try:
            if self.display:
                self.display.print_step("Generating architecture with AI...")
            spec = self.llm.generate_json(SYSTEM_PROMPT, user_prompt)
        except Exception as e:
            if self.display:
                self.display.print_error(f"LLM call failed: {e}")
            spec = self._generate_fallback_spec(description, style or "microservices", cloud)

        if self.display:
            self.display.print_step("Generating outputs...")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self._write_spec(spec, output_path)

        diagram = self.diagram_gen.generate(spec)
        self._write_file(output_path / "architecture.md", diagram)

        sql = self.schema_gen.generate(spec)
        self._write_file(output_path / "schema.sql", sql)

        openapi = self.api_gen.generate(spec)
        self._write_file(output_path / "openapi.yaml", openapi)

        tf = self.infra_gen.generate_terraform(spec)
        self._write_file(output_path / "main.tf", tf)

        docker_compose = self.infra_gen.generate_docker_compose(spec)
        self._write_file(output_path / "docker-compose.yml", docker_compose)

        dockerfile = self.infra_gen.generate_dockerfile(spec)
        self._write_file(output_path / "Dockerfile", dockerfile)

        env_example = self._generate_env_example(spec)
        self._write_file(output_path / ".env.example", env_example)

        readme = self._generate_readme(spec)
        self._write_file(output_path / "README.md", readme)

        if export_repo:
            if self.display:
                self.display.print_step("Packaging as GitHub-ready repo...")
            self.exporter.export(spec, output_path)

        if self.display:
            self.display.print_step("Architecture generation complete!")
            self.display.print_spec_summary(spec)

        return spec

    def _write_file(self, path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)

    def _write_spec(self, spec: dict, output_path: Path):
        import json
        self._write_file(output_path / "archon-spec.json", json.dumps(spec, indent=2))

    def _generate_env_example(self, spec: dict) -> str:
        lines = ["# Generated by Archon — https://github.com/Nortaq-PlayNexus/archon", ""]
        for var in spec.get("environment_variables", []):
            required = " # REQUIRED" if var.get("required", True) else " # optional"
            lines.append(f'{var["name"]}={var.get("description", "")}{required}')
        if not spec.get("environment_variables"):
            lines.append("# No environment variables detected for this architecture.")
        return "\n".join(lines) + "\n"

    def _generate_readme(self, spec: dict) -> str:
        name = spec.get("app_name", "Application")
        desc = spec.get("description", "")
        style = spec.get("style", "microservices")
        components = spec.get("components", [])

        comp_lines = []
        for c in components:
            comp_lines.append(f"| {c['name']} | {c.get('technology', '—')} | {c.get('purpose', '—')} | {c.get('type', '—')} |")

        comp_table = "\n".join(comp_lines) if comp_lines else "| (none) | — | — | — |"

        return f"""# {name}

> {desc}

**Architecture style:** {style}

## Architecture

See [architecture.md](architecture.md) for the visual diagram.

## Components

| Component | Technology | Purpose | Type |
|-----------|-----------|---------|------|
{comp_table}

## Quick Start

```bash
# Clone and configure
cp .env.example .env
# Edit .env with your values

# Start with Docker Compose
docker compose up -d
```

## Database

See [schema.sql](schema.sql) for the database schema.

## API

See [openapi.yaml](openapi.yaml) for the full API specification.

## Infrastructure

See [main.tf](main.tf) for Terraform configuration.

## Generated by [Archon](https://github.com/Nortaq-PlayNexus/archon)

This architecture was generated from a natural language description using AI.
"""

    def _generate_fallback_spec(self, description: str, style: str, cloud: str) -> dict:
        return {
            "app_name": description[:50].strip().title().replace(" ", "-"),
            "description": description,
            "style": style,
            "components": [
                {
                    "name": "api-gateway",
                    "type": "gateway",
                    "technology": "nginx",
                    "purpose": "Reverse proxy and rate limiting",
                    "ports": [80, 443],
                    "dependencies": ["app-server"],
                },
                {
                    "name": "app-server",
                    "type": "service",
                    "technology": "python:3.12-slim",
                    "purpose": "Application API server",
                    "ports": [8000],
                    "dependencies": ["database", "cache"],
                },
                {
                    "name": "database",
                    "type": "database",
                    "technology": "postgres:16",
                    "purpose": "Primary data store",
                    "ports": [5432],
                    "dependencies": [],
                },
                {
                    "name": "cache",
                    "type": "cache",
                    "technology": "redis:7-alpine",
                    "purpose": "Session and query cache",
                    "ports": [6379],
                    "dependencies": [],
                },
            ],
            "database_schema": {
                "tables": [
                    {
                        "name": "users",
                        "columns": [
                            {"name": "id", "type": "UUID", "primary_key": True, "nullable": False, "unique": True},
                            {"name": "email", "type": "VARCHAR(255)", "primary_key": False, "nullable": False, "unique": True},
                            {"name": "created_at", "type": "TIMESTAMPTZ", "primary_key": False, "nullable": False, "unique": False},
                        ],
                    }
                ]
            },
            "api_endpoints": [
                {"method": "GET", "path": "/health", "summary": "Health check", "request_body": {}, "response_example": {"status": "ok"}},
                {"method": "GET", "path": "/api/v1/items", "summary": "List items", "request_body": {}, "response_example": {"items": []}},
                {"method": "POST", "path": "/api/v1/items", "summary": "Create item", "request_body": {"name": "string"}, "response_example": {"id": "uuid", "name": "string"}},
            ],
            "infrastructure": {
                "cloud": cloud if cloud != "any" else "aws",
                "compute": "ecs",
                "database_service": "rds",
                "cache_service": "elasticache",
                "cdn": "cloudfront",
            },
            "environment_variables": [
                {"name": "DATABASE_URL", "description": "PostgreSQL connection string", "required": True},
                {"name": "REDIS_URL", "description": "Redis connection string", "required": True},
                {"name": "SECRET_KEY", "description": "Application secret key", "required": True},
            ],
        }
