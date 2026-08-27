# Example Deployment Request

Use a sanitized ticket like:

```text
Summary:
[DEPLOY] Add application subnet

Description:
Add the requested subnet to the existing Terraform network configuration.
Use the existing VNet and resource-group conventions.
```

Expected high-level outcome:

```text
Jira
  ↓
Function
  ↓
ACA Job
  ↓
Agent edits Terraform
  ↓
Feature branch
  ↓
Pull request
  ↓
Terraform Plan
  ↓
Merge
  ↓
Terraform Apply
  ↓
Jira work note + completion
```
