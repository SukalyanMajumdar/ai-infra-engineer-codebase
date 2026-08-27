# Implementation Inventory

This document records what was verified from the supplied codebase.

| Area | Verified implementation |
|---|---|
| Jira ingress | Azure Function HTTP endpoint with Function-level auth |
| Jira classification | `[DEPLOY]` and `[FIX]` summary prefixes |
| Azure handoff | `DefaultAzureCredential` + ARM API |
| ACA execution | Existing Container Apps Job template updated with `JIRA_PAYLOAD`, then started |
| Agent framework | LangChain `create_agent` |
| Model interface | `ChatOpenAI` with Responses API enabled |
| Repository tools | list/read/search/write |
| Repository safety | Prevent writes outside repo and inside `.git` |
| Git lifecycle | branch → commit → push |
| PR creation | GitHub CLI `gh pr create` |
| Terraform | init + plan in agent runtime; validate/plan/apply in Actions |
| Plan workflow | `workflow_dispatch` with feature-branch input |
| Apply workflow | push to `master` |
| Jira feedback | work note + transition lookup / completion transition |
| Fix agent | Not implemented in supplied runtime |
