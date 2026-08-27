# Security and Redaction

This repository is intended for public portfolio use.

## Never publish

- Azure client secrets
- GitHub tokens
- Jira API tokens
- OpenAI API keys
- Azure subscription IDs if they are considered sensitive in your environment
- Tenant IDs where organizational exposure is undesirable
- Private endpoints
- Internal hostnames
- Real backend storage account/container details
- Personal email addresses
- Internal repository URLs
- Private Jira URLs or ticket information

## Authentication boundaries in the implementation

### Function App

The HTTP trigger uses Function-level authentication. The Function uses `DefaultAzureCredential` to obtain an Azure Resource Manager token when starting the ACA Job.

### Agent runtime

The runtime expects GitHub and Azure credentials through environment variables. It uses `gh auth setup-git` for Git authentication and Azure CLI service-principal login for Terraform operations.

### GitHub Actions

Azure and Jira credentials are supplied through GitHub repository variables/secrets in the actual environment. The workflow source should remain public only after removing any environment-specific values.

### Terraform

Backend configuration is environment-specific and must not be committed to a public showcase repository when it contains real infrastructure identifiers.

## Public portfolio rule

The showcase repository documents **how the system works**, while the actual credentials and production configuration remain in the private runtime environment.
