# AI-Driven Infrastructure Deployment & Operations Platform

> **Jira → Azure Function → Azure Container Apps Job → AI Agent → GitHub → Terraform → Azure → Jira**

An event-driven AIOps platform that turns an infrastructure requirement in Jira into an AI-assisted Terraform change, validates it through GitHub Actions, deploys the approved infrastructure, and reports the deployment result back to Jira.

This repository is the **portfolio and architecture showcase** for the implementation. The production Terraform implementation remains in the dedicated infrastructure repository linked below.

---

## What this demonstrates

- **Event-driven automation** from Jira webhooks into Azure
- **Agentic infrastructure engineering** using LangChain and an OpenAI model
- **Repository-aware code changes**: the agent inspects the target Terraform repository before editing it
- **GitHub-native change control**: feature branch → commit → pull request
- **Terraform CI/CD** with plan and apply workflows
- **Azure authentication** using service credentials / workload configuration
- **Jira lifecycle integration** after deployment
- **Containerized execution** for the AI deployment runtime
- **Guardrails in the agent tool layer** around repository file access and `.git`

## Current implementation boundary

The current implementation has a concrete **`[DEPLOY]` path** end-to-end.

`[FIX]` tickets are recognized by the Jira Function App, but the current agent runtime explicitly reports that the incident/fix agent is not implemented yet. This showcase documents that boundary rather than claiming functionality that is not present.

---

## Project status

**Working implementation:** `[DEPLOY]` end-to-end path.  
**Documented extension:** `[FIX]` classification exists; incident remediation is not yet implemented.

## Architecture

```mermaid
flowchart TD
    J[Jira Issue\n[DEPLOY] / [FIX]]
    F[Azure Function App\nJira Webhook Gateway]
    A[Azure Container Apps Job\nAgent Runtime]
    L[LLM Agent\nLangChain + OpenAI]
    G[GitHub Repository\nTerraform]
    PR[Pull Request\nfeature/ai-<ticket>-attempt-<n>-<id>]
    P[GitHub Actions\nTerraform Plan]
    AP[GitHub Actions\nTerraform Apply]
    AZ[Azure Infrastructure]
    JR[Jira Work Note + Status Transition]

    J -->|Webhook POST| F
    F -->|Start job + JIRA_PAYLOAD| A
    A --> L
    L -->|inspect / edit| G
    A -->|branch, commit, push| G
    G --> PR
    PR -->|manual dispatch / validation| P
    PR -->|merge to master| AP
    AP -->|Terraform Apply| AZ
    AP -->|REST API| JR
    AZ --> JR
```

See [architecture.md](docs/architecture.md), [end-to-end-flow.md](docs/end-to-end-flow.md), and [implementation-inventory.md](docs/implementation-inventory.md) for the detailed design.

## End-to-end flow

1. An engineer creates a Jira issue whose summary begins with **`[DEPLOY]`**.
2. Jira sends the issue event to the Azure Function webhook endpoint.
3. The Function extracts the issue key, summary, description, target repository URL, and action.
4. The Function obtains an Azure management token through `DefaultAzureCredential`.
5. The Function reads the existing Azure Container Apps Job template and injects the serialized Jira payload as `JIRA_PAYLOAD`.
6. The Function starts an ACA Job execution.
7. The agent runtime parses the payload and invokes the deployment agent for `DEPLOY` requests.
8. The agent clones the target Terraform repository.
9. The agent creates a ticket-specific feature branch.
10. The LangChain agent inspects the repository and edits only the files required by the Jira request.
11. The runtime commits and pushes the changes.
12. Terraform is initialized and a plan is generated in the agent runtime.
13. A GitHub pull request is opened for the ticket.
14. GitHub Actions can execute the Terraform plan workflow against the feature branch.
15. After the approved PR is merged to `master`, the Terraform Apply workflow runs.
16. The Apply workflow adds a deployment work note to Jira and attempts the appropriate Done/Close transition.

## Implementation repositories

| Component | Repository / artifact |
|---|---|
| Terraform infrastructure | [ai-infra-engineer](https://github.com/SukalyanMajumdar/ai-infra-engineer/) |
| Jira webhook Function App | `1_jira_fnapp` implementation supplied for this showcase |
| ACA agent runtime | `2_agent_acaj` implementation supplied for this showcase |
| Portfolio documentation | This repository |

## Technology stack

**AI / Agent:** Python 3.14, LangChain Agents, OpenAI API

**Cloud:** Microsoft Azure, Azure Functions, Azure Container Apps Jobs, Azure Identity

**Infrastructure:** Terraform, AzureRM provider

**CI/CD:** GitHub, GitHub Actions, GitHub CLI

**ITSM / workflow:** Jira Cloud webhooks and REST API

**Runtime:** Docker containers, Python 3.14

## Security model

Secrets and environment-specific values are intentionally **not included** in this showcase repository.

The implementation expects configuration such as:

- Jira base URL / email / API token
- GitHub token
- OpenAI model configuration
- Azure service credentials / identity configuration
- Azure subscription and resource identifiers
- Terraform backend configuration

See [security.md](docs/security.md).

## Evidence

The strongest demonstration is a real execution trace:

**Jira ticket → Function invocation → ACA Job → Agent changes → GitHub PR → Terraform Plan → Merge → Terraform Apply → Jira work note/status**

Screenshots and sanitized execution evidence belong in [evidence/](evidence/). See [demo.md](docs/demo.md) for the recommended evidence sequence.

## Portfolio positioning

This project is best described as an **AI-driven AIOps / infrastructure automation platform**, not simply an AI code generator. The system connects an ITSM trigger, an agentic execution layer, source control, infrastructure-as-code, CI/CD, cloud authentication, and operational feedback into one workflow.
