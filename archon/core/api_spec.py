"""OpenAPI spec generator — produces YAML API specification."""

from typing import Any


class APISpecGenerator:
    def generate(self, spec: dict) -> str:
        endpoints = spec.get("api_endpoints", [])
        app_name = spec.get("app_name", "Application")
        description = spec.get("description", "")

        lines = [
            "openapi: 3.1.0",
            f"info:",
            f'  title: "{app_name} API"',
            f'  description: "{description}"',
            f"  version: 1.0.0",
            "servers:",
            "  - url: http://localhost:8000",
            "    description: Local development",
            "",
            "paths:",
        ]

        path_groups: dict[str, list[dict]] = {}
        for ep in endpoints:
            path = ep.get("path", "/")
            path_groups.setdefault(path, []).append(ep)

        for path, eps in sorted(path_groups.items()):
            lines.append(f"  {path}:")
            for ep in eps:
                method = ep.get("method", "GET").lower()
                summary = ep.get("summary", "")
                lines.append(f"    {method}:")
                lines.append(f'      summary: "{summary}"')

                req_body = ep.get("request_body")
                if req_body and isinstance(req_body, dict) and req_body:
                    lines.append("      requestBody:")
                    lines.append("        required: true")
                    lines.append("        content:")
                    lines.append("          application/json:")
                    lines.append("            schema:")
                    lines.append("              type: object")
                    lines.append("              properties:")
                    for k, v in req_body.items():
                        lines.append(f"                {k}:")
                        lines.append(f'                  type: "{self._map_type(v)}"')

                resp = ep.get("response_example", {})
                lines.append("      responses:")
                lines.append("        '200':")
                lines.append("          description: Success")
                if resp and isinstance(resp, dict) and resp:
                    lines.append("          content:")
                    lines.append("            application/json:")
                    lines.append("              schema:")
                    lines.append("                type: object")

            lines.append("")

        return "\n".join(lines)

    def _map_type(self, val: Any) -> str:
        if isinstance(val, bool):
            return "boolean"
        if isinstance(val, int):
            return "integer"
        if isinstance(val, float):
            return "number"
        if isinstance(val, list):
            return "array"
        return "string"
