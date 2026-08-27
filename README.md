# AI-Driven Infrastructure Automation Platform

### An AIOps workflow that turns a Jira infrastructure requirement into a controlled Azure deployment

---

## What I Built

I built an AI-driven infrastructure automation workflow that connects **Jira, Azure, GitHub, GitHub Actions, and Terraform**.

The workflow takes an infrastructure requirement from Jira, sends it through an AI agent running on Azure Container Apps, generates the required Terraform change, creates a GitHub pull request, and uses GitHub Actions to validate and deploy the infrastructure.

After deployment, the originating Jira ticket is updated with the deployment result.

### High-Level Flow

```text
Jira
  │
  │ Webhook
  ▼
Azure Function
  │
  │ Trigger
  ▼
Azure Container Apps Job
  │
  │ AI Agent
  ▼
GitHub Terraform Repository
  │
  │ Pull Request
  ▼
GitHub Actions
  │
  │ Terraform
  ▼
Azure Infrastructure
  │
  │ Result
  ▼
Jira
```

---

## Why This Is AIOps

The system connects **IT Service Management, AI-driven decision making, source control, CI/CD, Infrastructure as Code, and cloud infrastructure** into a single operational workflow.

Instead of manually translating a Jira requirement into Terraform and then manually executing the deployment, the platform automates the infrastructure-change lifecycle.

The AI agent is responsible for understanding the requirement and implementing the Terraform change.

The final infrastructure deployment remains inside the GitHub Actions and Terraform workflow.

This provides a clear separation between:

**AI-generated change**

and

**controlled infrastructure deployment**.

---

## Technology Stack

| Component              | Technology                |
| ---------------------- | ------------------------- |
| Requirement / ITSM     | Jira                      |
| Event Gateway          | Azure Functions           |
| AI Runtime             | Azure Container Apps Jobs |
| AI Framework           | LangChain                 |
| LLM                    | OpenAI                    |
| Source Control         | GitHub                    |
| CI/CD                  | GitHub Actions            |
| Infrastructure as Code | Terraform                 |
| Cloud                  | Microsoft Azure           |
| Application Language   | Python                    |
| Containerization       | Docker                    |

---

## Architecture

The system consists of four major stages:

### 1. Requirement

Jira acts as the entry point for an infrastructure request.

Example:

```text
[DEPLOY] Create a subnet
```

The Jira webhook provides the issue information required by the automation.

---

### 2. AI Infrastructure Engineering

The Azure Function receives the Jira webhook and starts the Azure Container Apps Job.

The agent receives the Jira issue information and works against the Terraform repository.

The agent can inspect the existing repository before making changes.

The resulting workflow is:

```text
Jira Requirement
       ↓
Azure Function
       ↓
ACA Job
       ↓
AI Agent
       ↓
Inspect Terraform
       ↓
Modify Terraform
```

---

### 3. Git-Based Deployment Workflow

The agent creates a feature branch, commits the Terraform changes, pushes the branch, and creates a GitHub pull request.

```text
AI Agent
   ↓
Feature Branch
   ↓
Commit
   ↓
Pull Request
```

The Jira issue key is carried through the Git workflow, providing traceability between the original requirement and the resulting infrastructure change.

---

### 4. Infrastructure Deployment

GitHub Actions handles the Terraform deployment lifecycle.

```text
Pull Request
      ↓
Terraform Validation / Plan
      ↓
Merge
      ↓
Terraform Apply
      ↓
Azure
```

After deployment, the GitHub Actions workflow updates the originating Jira issue with deployment information.

---

# End-to-End Example

A typical deployment looks like this:

```text
KAN-XX
[DEPLOY] Create Azure infrastructure
        │
        ▼
Jira Webhook
        │
        ▼
Azure Function
        │
        ▼
Azure Container Apps Job
        │
        ▼
AI Deploy Agent
        │
        ▼
Terraform Repository
        │
        ▼
GitHub Pull Request
        │
        ▼
GitHub Actions
        │
        ▼
Terraform
        │
        ▼
Azure Infrastructure
        │
        ▼
Jira Work Note
        │
        ▼
Jira Completed
```

The important property of this workflow is that the AI agent does not directly become the production deployment mechanism.

Instead, it produces a version-controlled infrastructure change that enters the existing GitHub/Terraform delivery process.

---

# Key Engineering Decisions

### AI is separated from final deployment

The AI agent handles infrastructure reasoning and Terraform modification.

GitHub Actions handles the final Terraform deployment.

This creates a controlled boundary between AI-generated changes and infrastructure execution.

### Infrastructure remains version controlled

All infrastructure changes are represented as Terraform code in GitHub.

This provides:

* Version history
* Pull requests
* Reviewability
* Traceability
* Reproducibility

### Jira remains the operational record

The Jira ticket is the starting point for the request and receives the resulting deployment information.

This creates a traceable relationship between:

```text
Requirement
    ↓
Infrastructure Change
    ↓
Deployment
    ↓
Operational Result
```

---

# Implementation

The Terraform implementation is maintained separately in GitHub:

**[Terraform Infrastructure Repository](https://github.com/SukalyanMajumdar/ai-infra-engineer/)**

The portfolio repository intentionally focuses on the **architecture, workflow, and execution evidence** rather than duplicating the complete implementation.

---

# Evidence

The `evidence/` directory contains screenshots from the working implementation.

The recommended evidence sequence is:

| #  | Evidence                |
| -- | ----------------------- |
| 01 | Jira deployment ticket  |
| 02 | GitHub pull request     |
| 03 | GitHub Actions workflow |
| 04 | Terraform execution     |
| 05 | Jira deployment result  |

These screenshots demonstrate the actual execution path rather than only describing the architecture.

Sensitive information should be redacted before publishing.

---

# Current Scope

### Implemented

* Jira webhook integration
* Jira requirement parsing
* `[DEPLOY]` request handling
* Azure Function integration
* Azure Container Apps Job execution
* LangChain AI agent
* OpenAI integration
* Terraform repository inspection
* AI-driven Terraform modification
* Git branch creation
* Git commit and push
* GitHub pull request creation
* Terraform planning
* GitHub Actions deployment
* Azure infrastructure deployment
* Jira deployment feedback

### Future Extension

The Jira integration also recognizes `[FIX]` requests.

The autonomous remediation workflow is not currently implemented end-to-end.

A future version can extend the platform to:

```text
Deployment Failure
       ↓
AI Diagnosis
       ↓
Automated Fix
       ↓
Terraform Change
       ↓
Pull Request
       ↓
Validation
       ↓
Deployment
```

---

# Project Value

This project demonstrates the integration of:

**AI Engineering**

* **AIOps**

* **Infrastructure as Code**

* **CI/CD**

* **Cloud Automation**

* **ITSM**

* **GitOps-style change control**

The key outcome is an automated path from a human infrastructure requirement to a controlled cloud infrastructure change.

---

## Project Status

**Deployment workflow:** Working

**AI infrastructure agent:** Working

**Terraform automation:** Working

**GitHub Actions deployment:** Working

**Jira integration:** Working

**Autonomous remediation:** Future work

---

### Core Workflow

> **Jira → AI → GitHub → Terraform → Azure → Jira**

