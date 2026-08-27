# ACA Agent Runtime

The supplied container runs the Python deployment agent as an Azure Container Apps Job execution.

The image includes:

- Python 3.14
- Git
- GitHub CLI
- Terraform
- Azure CLI
- LangChain dependencies

The runtime receives the Jira request through `JIRA_PAYLOAD`.
