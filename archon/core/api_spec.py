"""OpenAPI spec generator — produces YAML API specification."""

from typing import Any


class APISpecGenerator:
    def generate(self, spec: dict) -> str:
        endpoints = spec.get("api_endpoints", [])
        app_name = spec.get("app_name", "Application")
        description = spec.get("description", "")

        lines = [
            "openapi: 3.1.0",
            "info:",
            f'  title: "{app_name} API"',
            f'  description: "{description}"',
            "  version: 1.0.0",
            "servers:",
            "  - url: http://localhost:8000",
            "    description: Local development",
            "",
            "components:",
            "  securitySchemes:",
            "    bearerAuth:",
            "      type: http",
            "      scheme: bearer",
            "      bearerFormat: JWT",
            "    apiKey:",
            "      type: apiKey",
            "      in: header",
            "      name: X-API-Key",
            "",
            "  schemas:",
            "    Error:",
            "      type: object",
            "      required:",
            "        - code",
            "        - message",
            "      properties:",
            "        code:",
            "          type: integer",
            "          description: HTTP status code",
            "        message:",
            "          type: string",
            "          description: Error description",
            "        details:",
            "          type: object",
            "          description: Additional error context",
            "    ValidationError:",
            "      type: object",
            "      required:",
            "        - field",
            "        - message",
            "      properties:",
            "        field:",
            "          type: string",
            "        message:",
            "          type: string",
            "",
            "  parameters:",
            "    pageParam:",
            "      name: page",
            "      in: query",
            "      required: false",
            "      schema:",
            "        type: integer",
            "        default: 1",
            "        minimum: 1",
            "      description: Page number",
            "    limitParam:",
            "      name: limit",
            "      in: query",
            "      required: false",
            "      schema:",
            "        type: integer",
            "        default: 20",
            "        minimum: 1",
            "        maximum: 100",
            "      description: Items per page",
            "",
            "security:",
            "  - bearerAuth: []",
            "  - apiKey: []",
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
                tags = ep.get("tags", self._infer_tags(path))
                operation_id = ep.get("operation_id", self._generate_operation_id(method, path))

                lines.append(f"    {method}:")
                lines.append(f'      summary: "{summary}"')
                lines.append(f"      operationId: {operation_id}")

                if tags:
                    lines.append("      tags:")
                    for tag in tags:
                        lines.append(f"        - {tag}")

                if method in ("get", "delete") and "list" in path.lower():
                    lines.append("      parameters:")
                    lines.append("        - $ref: '#/components/parameters/pageParam'")
                    lines.append("        - $ref: '#/components/parameters/limitParam'")

                req_body = ep.get("request_body")
                if req_body and isinstance(req_body, dict) and req_body:
                    required_fields = ep.get("required_fields", list(req_body.keys()))
                    lines.append("      requestBody:")
                    lines.append("        required: true")
                    lines.append("        content:")
                    lines.append("          application/json:")
                    lines.append("            schema:")
                    lines.append("              type: object")
                    if required_fields:
                        lines.append("              required:")
                        for rf in required_fields:
                            lines.append(f"                - {rf}")
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

                lines.append("        '400':")
                lines.append("          description: Bad request")
                lines.append("          content:")
                lines.append("            application/json:")
                lines.append("              schema:")
                lines.append("                $ref: '#/components/schemas/Error'")
                lines.append("        '404':")
                lines.append("          description: Not found")
                lines.append("          content:")
                lines.append("            application/json:")
                lines.append("              schema:")
                lines.append("                $ref: '#/components/schemas/Error'")
                lines.append("        '500':")
                lines.append("          description: Internal server error")
                lines.append("          content:")
                lines.append("            application/json:")
                lines.append("              schema:")
                lines.append("                $ref: '#/components/schemas/Error'")

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

    def _infer_tags(self, path: str) -> list[str]:
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        if not parts:
            return ["default"]
        tags = []
        for part in parts[:2]:
            tags.append(part.replace("-", " ").replace("_", " ").title())
        return tags

    def _generate_operation_id(self, method: str, path: str) -> str:
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        name = "_".join(parts) if parts else "root"
        return f"{method}_{name}"
