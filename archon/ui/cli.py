"""Rich CLI interface for Archon."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
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
                "  archon info --stacks            Show supported stacks\n\n"
                "[bold]Options:[/bold]\n"
                "  --style   microservices|monolith|serverless|hybrid\n"
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
        ]
        for s, d in styles:
            table2.add_row(s, d)

        console.print(table2)
        console.print()
