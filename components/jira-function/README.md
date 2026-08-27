# Jira → Azure Function

The supplied Function App is the event gateway for the platform.

**Runtime:** Azure Functions / Python 3.14

**Trigger:** HTTP POST webhook

**Authentication:** Function-level trigger authentication

**Primary responsibility:** Normalize the Jira issue event and start an Azure Container Apps Job with the request payload.

See [Jira integration](../../docs/jira-integration.md).
