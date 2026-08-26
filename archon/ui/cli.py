"""Rich CLI interface for Archon."""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box


console = Console()


class CLIDisplay:
    def print_welcome(self):
        console.print()
        console.print(
            Panel(
                "[bold cyan]Archon[/bold cyan] — AI System Architect\n\n"
                "Describe your application in plain English.\n"
                "Archon generates the complete architecture package:\n"
                "  diagrams, schemas, IaC, Docker configs, and more.",
                border_style="blue",
                expand=True,
            )
        )
        console.print()

    def prompt_description(self) -> str:
        console.print("[dim]Describe your application (be specific about features, scale, and tech preferences):[/dim]")
        console.print()
        lines = []
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                break
            if line.strip() == "" and lines:
                break
            lines.append(line)
        return "\n".join(lines).strip()

    def print_step(self, message: str):
        console.print(f"  [bold blue]→[/bold blue] {message}")

    def print_success(self, message: str):
        console.print(f"  [bold green]✓[/bold green] {message}")

    def print_error(self, message: str):
        console.print(f"  [bold red]✗[/bold red] {message}")

    def print_spec_summary(self, spec: dict):
        console.print()

        name = spec.get("app_name", "Unknown")
        style = spec.get("style", "unknown")
        components = spec.get("components", [])
        endpoints = spec.get("api_endpoints", [])
        tables = spec.get("database_schema", {}).get("tables", [])

        table = Table(box=box.ROUNDED, title=f"{name} — Generated Architecture")
        table.add_column("Metric", style="bold")
        table.add_column("Value", style="cyan")
        table.add_row("Architecture Style", style)
        table.add_row("Components", str(len(components)))
        table.add_row("API Endpoints", str(len(endpoints)))
        table.add_row("Database Tables", str(len(tables)))
        table.add_row("Output Files", "10+")

        console.print(table)

        if components:
            console.print()
            ctable = Table(box=box.SIMPLE_HEAVY, title="Components")
            ctable.add_column("Name", style="cyan")
            ctable.add_column("Type")
            ctable.add_column("Technology")
            ctable.add_column("Purpose")
            for c in components:
                ctable.add_row(
                    c["name"],
                    c.get("type", "—"),
                    c.get("technology", "—"),
                    c.get("purpose", "—"),
                )
            console.print(ctable)

        console.print()

    def print_info(self):
        console.print()
        console.print(
            Panel(
                "[bold cyan]Archon[/bold cyan] — AI System Architect\n\n"
                "Transform natural language descriptions into complete\n"
                "system architectures with diagrams, schemas, and IaC.\n\n"
                "[bold]Commands:[/bold]\n"
                "  archon generate <description>   Generate architecture\n"
                "  archon generate --interactive   Interactive mode\n"
                "  archon validate <spec-file>     Validate a spec file\n"
                "  archon info --stacks            Show supported stacks\n\n"
                "[bold]Options:[/bold]\n"
                "  --style   microservices|monolith|serverless|hybrid|event-driven|cqrs\n"
                "  --cloud   aws|gcp|azure|any\n"
                "  --export-repo  Package as GitHub-ready repo",
                border_style="blue",
                expand=True,
            )
        )
        console.print()

    def print_supported_stacks(self):
        console.print()
        table = Table(box=box.ROUNDED, title="Supported Tech Stacks")
        table.add_column("Language", style="cyan")
        table.add_column("Runtime")
        table.add_column("Docker Base Image")

        stacks = [
            ("Python", "3.11+", "python:3.12-slim"),
            ("Node.js", "20+", "node:20-alpine"),
            ("Go", "1.22+", "golang:1.22-alpine"),
            ("Rust", "1.77+", "rust:1.77-slim"),
            ("Java", "21+", "eclipse-temurin:21-jre"),
            ("Ruby", "3.3+", "ruby:3.3-slim"),
        ]
        for lang, runtime, docker in stacks:
            table.add_row(lang, runtime, docker)

        console.print(table)

        table2 = Table(box=box.ROUNDED, title="Supported Architecture Styles")
        table2.add_column("Style", style="cyan")
        table2.add_column("Description")

        styles = [
            ("microservices", "独立服务通过 API 通信，适合团队和规模化"),
            ("monolith", "单体应用，适合 MVP 和小团队"),
            ("serverless", "函数即服务，按调用付费，零运维"),
            ("hybrid", "混合架构，核心服务 + serverless 边缘"),
            ("event-driven", "事件驱动架构，异步消息，最终一致性"),
            ("cqrs", "命令查询职责分离，读写模型分离"),
        ]
        for s, d in styles:
            table2.add_row(s, d)

        console.print(table2)
        console.print()

    def validate_spec(self, spec_path: str):
        path = Path(spec_path)
        if not path.exists():
            self.print_error(f"File not found: {spec_path}")
            return False

        try:
            with open(path, "r") as f:
                spec = json.load(f)
        except json.JSONDecodeError as e:
            self.print_error(f"Invalid JSON: {e}")
            return False

        errors = []
        warnings = []

        required_fields = {
            "app_name": "string",
            "description": "string",
            "style": "string",
            "components": "list",
            "database_schema": "object",
            "api_endpoints": "list",
            "infrastructure": "object",
            "environment_variables": "list",
        }

        for field, expected_type in required_fields.items():
            if field not in spec:
                errors.append(f"Missing required field: '{field}'")
            elif expected_type == "list" and not isinstance(spec[field], list):
                errors.append(f"'{field}' must be a list, got {type(spec[field]).__name__}")
            elif expected_type == "object" and not isinstance(spec[field], dict):
                errors.append(f"'{field}' must be an object, got {type(spec[field]).__name__}")

        if "components" in spec and isinstance(spec["components"], list):
            for i, comp in enumerate(spec["components"]):
                if "name" not in comp:
                    errors.append(f"Component at index {i} missing 'name'")
                if "type" not in comp:
                    errors.append(f"Component '{comp.get('name', f'index {i}')}' missing 'type'")
                if "technology" not in comp:
                    warnings.append(f"Component '{comp.get('name', f'index {i}')}' missing 'technology'")

        if "database_schema" in spec and isinstance(spec["database_schema"], dict):
            tables = spec["database_schema"].get("tables", [])
            if not tables:
                warnings.append("No tables defined in database_schema")
            for i, table in enumerate(tables):
                if "name" not in table:
                    errors.append(f"Table at index {i} missing 'name'")
                if "columns" not in table:
                    warnings.append(f"Table '{table.get('name', f'index {i}')}' has no columns defined")

        if "api_endpoints" in spec and isinstance(spec["api_endpoints"], list):
            for i, ep in enumerate(spec["api_endpoints"]):
                if "path" not in ep:
                    errors.append(f"Endpoint at index {i} missing 'path'")
                if "method" not in ep:
                    errors.append(f"Endpoint at index {i} missing 'method'")

        console.print()
        table = Table(box=box.ROUNDED, title=f"Validation Report: {path.name}")
        table.add_column("Check", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Details")

        table.add_row("JSON Syntax", "[green]✓[/green]" if not errors else "[red]✗[/red]", "Valid" if not errors else f"{len(errors)} errors")

        for field in required_fields:
            status = "[green]✓[/green]" if field in spec else "[red]✗[/red]"
            detail = "Present" if field in spec else "Missing"
            table.add_row(f"  {field}", status, detail)

        if spec.get("components"):
            table.add_row("Components", "[green]✓[/green]", f"{len(spec['components'])} defined")
        if spec.get("api_endpoints"):
            table.add_row("API Endpoints", "[green]✓[/green]", f"{len(spec['api_endpoints'])} defined")
        if spec.get("database_schema", {}).get("tables"):
            table.add_row("DB Tables", "[green]✓[/green]", f"{len(spec['database_schema']['tables'])} defined")

        console.print(table)

        if errors:
            console.print()
            self.print_error("Validation Errors:")
            for err in errors:
                console.print(f"    [red]✗[/red] {err}")

        if warnings:
            console.print()
            console.print("  [bold yellow]Warnings:[/bold yellow]")
            for warn in warnings:
                console.print(f"    [yellow]![/yellow] {warn}")

        console.print()
        if not errors:
            self.print_success(f"Spec '{path.name}' is valid!")
        else:
            self.print_error(f"Spec '{path.name}' has {len(errors)} error(s)")
        console.print()

        return len(errors) == 0
