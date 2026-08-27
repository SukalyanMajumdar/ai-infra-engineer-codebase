# Agent Workflow

## Agent objective

The deployment agent is instructed to act as a Terraform infrastructure engineer working inside a cloned repository.

The system prompt emphasizes:

- inspect before changing
- change only what the ticket requires
- understand the existing Terraform structure
- do not modify `.git`
- do not invent requirements
- use only supplied repository tools
- do not directly run Git or Terraform commands through the agent tool layer

## Tool surface

| Tool | Purpose |
|---|---|
| `list_files` | Inspect repository structure |
| `read_file` | Read Terraform/configuration files |
| `search_files` | Find relevant resources/patterns |
| `write_file` | Create or update repository files |

The tool layer validates repository paths and blocks writes outside the repository root and inside `.git`.

## Deterministic operations around the agent

The LLM is responsible for reasoning about repository changes. The surrounding application code is responsible for deterministic operations such as:

```text
clone
branch creation
commit
push
Azure login
Terraform init
Terraform plan
PR creation
```

This separation is intentional: the agent proposes/implements repository changes through constrained tools, while the execution framework controls the operational lifecycle.

## Current limitation

The current `FIX` action is recognized by the Function App but the agent runtime reports that the incident/fix agent is not implemented. The portfolio should preserve this fact rather than presenting the fix workflow as complete.
