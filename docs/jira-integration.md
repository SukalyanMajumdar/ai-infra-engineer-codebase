# Jira Integration

## Incoming direction

Jira sends a webhook event to the Azure Function App.

The current implementation reads:

```text
issue.key
issue.fields.summary
issue.fields.description
```

The summary prefix controls the action classification:

```text
[DEPLOY] → DEPLOY
[FIX]    → FIX
```

The Function then passes the normalized payload into the ACA Job.

## Outgoing direction

After a successful Terraform Apply, GitHub Actions calls Jira's REST API using the ticket key extracted from the merged PR branch.

The workflow records:

- deployment completion
- GitHub repository
- commit SHA

It then attempts to transition the Jira issue to a completion state.

## Portfolio evidence

Use screenshots of:

1. The Jira ticket before automation.
2. The ticket after the PR is created.
3. The ticket after Terraform Apply.
4. The Jira work note showing the deployment result.
5. The final issue status.

Redact domains, usernames, email addresses, tokens, and any organization-specific information before publishing.
