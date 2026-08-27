# End-to-End Execution Flow

## Deployment request

### Stage 1 — Jira

Example requirement:

```text
Summary: [DEPLOY] Create a new application subnet
Description: Add the requested subnet to the Terraform infrastructure repository.
```

The webhook payload contains the issue key and fields required by the automation.

### Stage 2 — Function App

The Function extracts:

```text
ticket_id
summary
description
repo_url
action
```

It then creates a normalized payload:

```json
{
  "ticket_id": "KAN-123",
  "summary": "[DEPLOY] Create a new application subnet",
  "description": "...",
  "repo_url": "<target repository>",
  "action": "DEPLOY"
}
```

The payload is passed to the ACA Job as the `JIRA_PAYLOAD` environment variable.

### Stage 3 — Agent execution

The ACA Job starts the Python runtime. For a `DEPLOY` action, the deployment agent:

1. Clones the repository.
2. Configures Git/GitHub authentication.
3. Creates a feature branch.
4. Starts the LangChain agent.
5. Lets the agent inspect the repository.
6. Lets the agent edit required files through the repository tools.
7. Commits and pushes the result.
8. Logs into Azure.
9. Runs Terraform initialization.
10. Runs Terraform plan.
11. Creates the GitHub pull request.

### Stage 4 — GitHub Actions

The Plan workflow can be manually dispatched with the feature branch as an input.

It performs:

```text
checkout feature branch
        ↓
Azure login
        ↓
Terraform setup
        ↓
Terraform init
        ↓
Terraform validate
        ↓
Terraform plan
        ↓
Terraform plan JSON artifact
```

### Stage 5 — Apply

After the pull request is merged into `master`, the Apply workflow:

```text
checkout master
        ↓
Azure login
        ↓
Terraform setup
        ↓
Terraform init
        ↓
Terraform validate
        ↓
Terraform apply -auto-approve
```

### Stage 6 — Jira feedback

The Apply workflow derives the Jira key from the merged PR branch using the `KAN-<number>` pattern.

It then:

1. Adds a deployment-completed work note to the Jira issue.
2. Queries available Jira transitions.
3. Selects a `Done`, `Close`, or `Closed` transition when available.
4. Transitions the issue.

This closes the operational loop:

```text
Requirement → Change → Validation → Deployment → ITSM confirmation
```
