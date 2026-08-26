"""Archon — CLI entry point."""

import argparse
import sys

from archon import __version__
from archon.config import load_config
from archon.core.architect import Architect
from archon.ui.cli import CLIDisplay


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="archon",
        description="AI System Architect — describe your app, get the entire backend.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate architecture from description")
    gen.add_argument("description", nargs="?", help="Natural language app description")
    gen.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    gen.add_argument("--output", "-o", type=str, default="./archon-output", help="Output directory")
    gen.add_argument(
        "--style",
        choices=["microservices", "monolith", "serverless", "hybrid"],
        default=None,
        help="Architecture style (auto-detected if omitted)",
    )
    gen.add_argument(
        "--cloud",
        choices=["aws", "gcp", "azure", "any"],
        default="any",
        help="Target cloud provider",
    )
    gen.add_argument(
        "--export-repo", action="store_true", help="Export as a complete GitHub-ready repo"
    )

    info = sub.add_parser("info", help="Show supported stacks and options")
    info.add_argument("--stacks", action="store_true", help="List supported tech stacks")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    config = load_config()
    display = CLIDisplay()

    if args.command == "info":
        if args.stacks:
            display.print_supported_stacks()
        else:
            display.print_info()
        return 0

    if args.command == "generate":
        description = args.description
        if not description or args.interactive:
            display.print_welcome()
            description = display.prompt_description()
            if not description:
                display.print_error("No description provided.")
                return 1

        architect = Architect(config=config, display=display)
        result = architect.generate(
            description=description,
            style=args.style,
            cloud=args.cloud,
            output_dir=args.output,
            export_repo=args.export_repo,
        )

        if result:
            display.print_success(f"Architecture generated in {args.output}/")
            return 0
        else:
            display.print_error("Generation failed.")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
