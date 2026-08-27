# Demo and Evidence Plan

A strong portfolio demonstration should show one real `[DEPLOY]` execution from beginning to end.

## Recommended 2–4 minute demo

1. Show the Jira ticket.
2. Show the Function App receiving the webhook or its execution log.
3. Show the ACA Job execution.
4. Show the agent inspecting/modifying the Terraform repository.
5. Show the generated feature branch and pull request.
6. Show the Terraform Plan workflow.
7. Merge the PR.
8. Show the Terraform Apply workflow.
9. Show the resulting Azure resource change.
10. Show the Jira work note and final status.

## Evidence folder

Place sanitized screenshots in `evidence/` using descriptive names such as:

```text
01-jira-request.png
02-function-webhook.png
03-agent-execution.png
04-github-pr.png
05-terraform-plan.png
06-terraform-apply.png
07-jira-completed.png
```

Do not commit secrets or unredacted internal information.
