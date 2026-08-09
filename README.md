<div align="center">

# Archon

**Describe your app in plain English. Get the entire backend — diagrams, schemas, IaC, Docker configs, and deploy-ready code.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/LLM-OpenAI_API-412991?logo=openai&logoColor=white)](https://openai.com)

</div>

**Archon** is an AI system architect that takes a plain-English description of your application and generates a complete architecture package: component diagrams, database schemas, API specs, Terraform IaC, Docker configurations, and a GitHub-ready project structure.

No more whiteboard sessions. No more "let me think about the architecture." Just describe what you want and deploy it.

---

## What it generates

| Output | Description |
|---|---|
| `architecture.md` | Visual Mermaid diagram + component table + data flow |
| `schema.sql` | Full SQL DDL with tables, indexes, and constraints |
| `openapi.yaml` | OpenAPI 3.1 spec with all endpoints |
| `main.tf` | Terraform config (AWS/GCP/Azure) |
| `docker-compose.yml` | Local development stack |
| `Dockerfile` | Optimized multi-stage build |
| `.env.example` | Environment variables |
| `README.md` | Project documentation |
| `archon-spec.json` | Raw architecture spec (machine-readable) |

Plus optional GitHub scaffolding: LICENSE, CONTRIBUTING, SECURITY, PR templates.

---

## Quick start

```bash
# Install
pip install -e .

# Set your OpenAI key
export OPENAI_API_KEY=sk-...

# Generate from a description
archon generate "A real-time collaborative document editor with auth, versioning, and live cursors"

# Interactive mode
archon generate --interactive

# Target a specific cloud
archon generate "E-commerce API" --cloud aws --style microservices

# Export as a full GitHub repo
archon generate "Blog platform" --export-repo --output ./my-blog
```

---

## Examples

### Simple API

```bash
archon generate "REST API for a task manager with users, projects, and tasks. JWT auth, PostgreSQL, Redis cache."
```

### Complex system

```bash
archon generate "A real-time ride-sharing app like Uber. Needs: user app, driver app, matching service, payment processing, location tracking, surge pricing, and an admin dashboard. Microservices on AWS."
```

### Serverless

```bash
archon generate "Image processing pipeline. Upload to S3, trigger Lambda for resize/watermark, store thumbnails in DynamoDB, serve via CloudFront CDN." --style serverless --cloud aws
```

---

## How it works

```
Natural Language Description
         │
         ▼
    ┌─────────┐
    │  Archon  │ ◄── LLM (GPT-4o / any OpenAI-compatible API)
    └────┬────┘
         │
         ├──► architecture.md    (Mermaid diagrams + component details)
         ├──► schema.sql         (SQL DDL with indexes)
         ├──► openapi.yaml       (OpenAPI 3.1 spec)
         ├──► main.tf            (Terraform IaC)
         ├──► docker-compose.yml (Local dev stack)
         ├──► Dockerfile         (Optimized build)
         ├──► .env.example       (Required env vars)
         ├──► README.md          (Project documentation)
         └──► archon-spec.json   (Raw spec)
```

---

## Architecture styles

| Style | When to use |
|---|---|
| `microservices` | Teams, scale, independent deployments |
| `monolith` | MVPs, small teams, simple domains |
| `serverless` | Event-driven, variable load, zero ops |
| `hybrid` | Core services + serverless edge functions |

---

## Cloud providers

| Provider | Compute | Database | Cache | CDN |
|---|---|---|---|---|
| **AWS** | ECS Fargate | RDS | ElastiCache | CloudFront |
| **GCP** | Cloud Run | Cloud SQL | Memorystore | Cloud CDN |
| **Azure** | Container Instances | Azure SQL | Azure Cache | Azure CDN |

---

## Requirements

- Python 3.11+
- OpenAI API key (or any OpenAI-compatible endpoint)
- `requests`, `rich`, `pyyaml`

---

## Configuration

Create `~/.config/archon/config.json`:

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4o",
  "llm_base_url": "https://api.openai.com/v1",
  "temperature": 0.3,
  "max_tokens": 4096
}
```

Or use environment variables:

```bash
export OPENAI_API_KEY=sk-...
export ARCHON_OPENAI_KEY=sk-...    # takes precedence
```

---

## License

[MIT](LICENSE) — PlayNexus
