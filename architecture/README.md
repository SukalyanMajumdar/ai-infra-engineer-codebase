# System Architecture

## Overview

The AI-Driven Infrastructure Automation Platform is an event-driven infrastructure delivery system that connects an ITSM platform, an AI agent runtime, source control, CI/CD, Infrastructure as Code, and cloud infrastructure.

The architecture separates the workflow into distinct responsibilities:

```text
┌──────────────────────┐
│        Jira          │
│ Requirement / ITSM   │
└──────────┬───────────┘
           │
           │ Webhook
           ▼
┌──────────────────────┐
│   Azure Function     │
│ Event Processing     │
└──────────┬───────────┘
           │
           │ Azure Management API
           ▼
┌──────────────────────┐
│ Azure Container Apps │
│        Job           │
│   Agent Runtime      │
└──────────┬───────────┘
           │
           │
           ▼
┌──────────────────────┐
│      AI Agent        │
│  LangChain + OpenAI  │
└──────────┬───────────┘
           │
           │ Git / GitHub API
           ▼
┌──────────────────────┐
│       GitHub         │
│ Terraform Repository │
└──────────┬───────────┘
           │
           │ Pull Request
           ▼
┌──────────────────────┐
│   GitHub Actions     │
│ Terraform CI/CD      │
└──────────┬───────────┘
           │
           │ Terraform
           ▼
┌──────────────────────┐
│        Azure         │
│ Target Infrastructure│
└──────────┬───────────┘
           │
           │ Result
           ▼
┌──────────────────────┐
│        Jira          │
│ Work Note / Status   │
└──────────────────────┘
```

---

# Architectural Layers

The platform can be divided into six logical layers.

## 1. ITSM Layer

**Technology:** Jira

Jira represents the operational requirement.

An engineer creates a ticket containing the desired infrastructure change.

The ticket acts as the source of truth for the request.

Example:

```text
KAN-28

[DEPLOY] Create a subnet

Description:
Create a subnet with the requested configuration
in the existing Terraform infrastructure.
```

The Jira issue key becomes the primary correlation identifier throughout the workflow.

---

## 2. Event Processing Layer

**Technology:** Azure Functions

The Azure Function provides the HTTP-facing integration boundary.

Its responsibilities are intentionally limited to request processing and orchestration.

```text
Jira
  │
  │ HTTP POST
  ▼
Function App
  │
  ├── Parse webhook payload
  ├── Extract issue key
  ├── Extract summary
  ├── Extract description
  ├── Determine requested action
  └── Build agent payload
```

The Function App does not implement the infrastructure reasoning itself.

This keeps the integration layer independent from the AI runtime.

---

# 3. AI Execution Layer

**Technology:** Azure Container Apps Jobs + Python + LangChain + OpenAI

The AI execution layer is deployed as an Azure Container Apps Job.

The Function App starts an execution of the job and passes the Jira request through the `JIRA_PAYLOAD` environment variable.

The runtime then:

1. Reads the request.
2. Parses the requested action.
3. Routes deployment requests to the deployment agent.
4. Initializes the repository workspace.
5. Provides the agent with repository tools.
6. Allows the agent to inspect the Terraform code.
7. Allows the agent to make the required Terraform modifications.
8. Creates a Git branch.
9. Commits and pushes the change.
10. Runs Terraform initialization and planning.
11. Creates a GitHub pull request.

The AI runtime therefore functions as an **infrastructure-change implementation layer** rather than as the final infrastructure execution engine.

---

# 4. Source-Control Layer

**Technology:** GitHub

The Terraform repository provides the source-control boundary for infrastructure changes.

The agent interacts with the repository using Git and GitHub APIs.

The workflow is designed around feature branches.

Example:

```text
feature/ai-KAN-28-attempt-1-a1b2c3
```

The branch name contains the originating Jira issue key.

The resulting commit also contains the Jira identifier:

```text
KAN-28: deployment attempt 1
```

The pull request uses the Jira identifier as well:

```text
KAN-28: deployment
```

This creates a traceable relationship between:

```text
Jira
  ↓
Branch
  ↓
Commit
  ↓
Pull Request
```

---

# 5. CI/CD Layer

**Technology:** GitHub Actions

GitHub Actions provides the controlled execution path for Terraform.

The CI/CD layer is intentionally separated from the AI agent.

The AI agent creates the infrastructure change and pull request.

GitHub Actions performs the repository-controlled infrastructure workflow.

This separation provides an important governance boundary:

```text
AI Agent
   │
   │ Generates infrastructure change
   ▼
GitHub Pull Request
   │
   │ Controlled repository workflow
   ▼
GitHub Actions
   │
   │ Executes Terraform
   ▼
Azure
```

---

# 6. Infrastructure Layer

**Technology:** Terraform + Azure

Terraform is the Infrastructure as Code layer.

The Terraform repository defines reusable modules for Azure infrastructure components.

The current implementation includes modules for:

```text
modules/
├── resource_group
├── vnet
├── subnet
├── storage_account
├── nsg
└── nsg_rule
```

The root Terraform configuration composes these modules and supplies the required relationships and variables.

The deployment workflow therefore maintains infrastructure as declarative, version-controlled code.

---

# Component Responsibilities

## Jira

**Responsibility:** Requirement and operational record.

Jira:

* Stores the infrastructure requirement.
* Generates the webhook event.
* Provides the issue key.
* Provides the summary.
* Provides the description.
* Receives deployment feedback.
* Receives the resulting work note.
* Is transitioned after deployment.

---

## Azure Function App

**Responsibility:** Event gateway and orchestration.

The Function App:

* Receives the Jira webhook.
* Determines whether the request is supported.
* Extracts the required Jira fields.
* Creates the structured agent request.
* Authenticates to Azure.
* Starts the Container Apps Job.

The Function App is not responsible for editing Terraform.

---

## Azure Container Apps Job

**Responsibility:** Ephemeral AI execution environment.

The Container Apps Job:

* Provides the execution environment for the agent.
* Receives the Jira request.
* Executes the Python agent runtime.
* Provides the temporary repository workspace.
* Executes the deployment workflow.
* Terminates after the job completes.

This is preferable to requiring a permanently running agent process for an event-driven deployment request.

---

## AI Agent

**Responsibility:** Infrastructure reasoning and repository modification.

The deployment agent:

* Interprets the Jira requirement.
* Inspects the repository.
* Determines the required Terraform changes.
* Modifies Terraform files.
* Creates the feature branch.
* Commits the changes.
* Pushes the branch.
* Initializes Terraform.
* Creates a Terraform plan.
* Creates the pull request.

The agent does not directly perform the final production Terraform Apply.

---

## GitHub

**Responsibility:** Version control and change management.

GitHub provides:

* Repository storage.
* Feature branches.
* Commits.
* Pull requests.
* GitHub Actions execution.
* Deployment history.

---

## GitHub Actions

**Responsibility:** Controlled CI/CD execution.

GitHub Actions provides:

* Terraform formatting/validation.
* Terraform planning.
* Terraform application.
* Azure authentication.
* Jira feedback after deployment.

---

## Terraform

**Responsibility:** Declarative infrastructure management.

Terraform converts the version-controlled configuration into the desired Azure infrastructure state.

---

## Azure

**Responsibility:** Cloud infrastructure and platform execution.

Azure hosts:

* The Function App.
* The Container Apps Job.
* The target infrastructure managed through Terraform.

---

# Authentication Boundaries

Each integration has its own authentication mechanism.

```text
Jira
  │
  │ Function authentication
  ▼
Azure Function
  │
  │ Azure identity / management API
  ▼
Container Apps Job
  │
  │ GitHub token
  ▼
GitHub
  │
  │ GitHub Actions Azure credentials
  ▼
Azure
```

This avoids treating the entire system as a single unrestricted trust boundary.

---

# Function App → Container Apps Architecture

The Function App does not simply send an HTTP request to a long-running AI server.

Instead, it uses the Azure management API to start a Container Apps Job execution.

The process is:

```text
Jira Webhook
     │
     ▼
Azure Function
     │
     ├── Authenticate with Azure
     │
     ├── Retrieve Job configuration
     │
     ├── Inject JIRA_PAYLOAD
     │
     └── Start Job
             │
             ▼
       Container Apps Job
             │
             ▼
          AI Agent
```

This allows each Jira event to result in an isolated agent execution.

---

# AI Agent Tool Boundary

The deployment agent does not receive unrestricted infrastructure shell access through the LLM tool interface.

Instead, repository interaction is exposed through dedicated tools.

The primary operations include:

```text
list_files
read_file
search_files
write_file
```

This means the LLM operates through an explicit tool interface for repository modification.

The surrounding Python runtime retains control over operations such as:

```text
Git
Terraform
GitHub
Azure authentication
```

This separation reduces the amount of unrestricted operational authority exposed directly to the language model.

---

# GitHub Change Boundary

The AI-generated infrastructure change passes through GitHub before final deployment.

```text
AI Agent
   │
   ▼
Feature Branch
   │
   ▼
Commit
   │
   ▼
Pull Request
   │
   ▼
Terraform Plan
   │
   ▼
Merge
   │
   ▼
Terraform Apply
```

This provides a natural governance point where the infrastructure change can be inspected before it reaches the target environment.

---

# Terraform State Architecture

Terraform uses the AzureRM backend.

The configuration contains:

```hcl
backend "azurerm" {}
```

Backend-specific configuration is supplied separately.

This keeps environment-specific state configuration outside the main Terraform source.

The actual backend values are intentionally excluded from the public showcase.

---

# Operational Traceability

The Jira issue key is the correlation identifier.

Example:

```text
KAN-28
```

The identifier is propagated through:

```text
Jira Issue
    │
    ▼
Function Payload
    │
    ▼
Agent Execution
    │
    ▼
Git Branch
    │
    ▼
Git Commit
    │
    ▼
Pull Request
    │
    ▼
GitHub Actions
    │
    ▼
Jira Work Note
```

This allows an operator to trace an infrastructure change back to the originating operational requirement.

---

# Failure Boundaries

Failures can occur at several stages:

```text
Jira
 │
 ├── Webhook failure
 │
 ▼
Function App
 │
 ├── Payload validation failure
 ├── Azure API failure
 │
 ▼
Container Apps Job
 │
 ├── Agent execution failure
 ├── Repository failure
 ├── Terraform plan failure
 │
 ▼
GitHub
 │
 ├── Push failure
 └── Pull request failure
 │
 ▼
GitHub Actions
 │
 ├── Validation failure
 ├── Plan failure
 └── Apply failure
 │
 ▼
Azure
```

The current implementation provides a concrete deployment path and explicit error handling at multiple integration boundaries.

A future remediation agent can consume deployment failures and attempt an automated corrective workflow.

---

# Current Deployment Architecture

The currently implemented deployment path is:

```text
Jira
  │
  │ [DEPLOY]
  ▼
Azure Function
  │
  │ JIRA_PAYLOAD
  ▼
Azure Container Apps Job
  │
  ▼
LangChain Agent
  │
  │ Repository tools
  ▼
Terraform Repository
  │
  │ Git branch / commit / push
  ▼
GitHub Pull Request
  │
  ▼
Terraform Plan
  │
  ▼
Merge
  │
  ▼
Terraform Apply
  │
  ▼
Azure Infrastructure
  │
  ▼
Jira Work Note
  │
  ▼
Jira Completion
```

---

# Design Rationale

## Why Jira?

Jira provides a natural ITSM entry point for infrastructure requirements and maintains the operational record associated with the change.

## Why Azure Functions?

The Function App provides a lightweight event-driven boundary between Jira and the agent runtime.

## Why Azure Container Apps Jobs?

The workload is event-driven and execution-oriented. A job provides an isolated execution environment for each request without requiring the AI runtime to remain continuously active.

## Why an AI Agent?

Infrastructure requirements often require repository inspection and contextual reasoning before the correct Terraform change can be determined.

The agent can inspect the existing Terraform structure before modifying it.

## Why GitHub Pull Requests?

The pull request creates a change-control boundary between AI-generated code and infrastructure deployment.

## Why GitHub Actions?

GitHub Actions provides a repository-native CI/CD mechanism for validating and applying Terraform changes.

## Why Terraform?

Terraform provides declarative, version-controlled Infrastructure as Code with a well-defined plan/apply lifecycle.

---

# Architecture Boundary

The most important boundary in the system is:

```text
┌───────────────────────────────┐
│       AI CHANGE GENERATION    │
│                               │
│ Jira → Agent → Terraform Code │
└───────────────┬───────────────┘
                │
                │ Pull Request
                ▼
┌───────────────────────────────┐
│       DEPLOYMENT CONTROL      │
│                               │
│ GitHub Actions → Terraform    │
│ → Azure                       │
└───────────────────────────────┘
```

This architecture prevents the AI agent from being the sole authority responsible for both generating and executing an infrastructure change.

The result is a more traceable and governable model for AI-assisted infrastructure automation.

