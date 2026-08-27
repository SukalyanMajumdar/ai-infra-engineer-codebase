# Terraform Infrastructure Layer

The Terraform implementation is maintained separately in:

https://github.com/SukalyanMajumdar/ai-infra-engineer/

The supplied repository uses a modular root configuration with these modules:

```text
modules/
├── nsg/
├── nsg_rule/
├── resource_group/
├── storage_account/
├── subnet/
└── vnet/
```

The root module composes these modules and passes normalized local structures into them.

The deployment agent targets this repository rather than embedding infrastructure definitions inside the agent itself. This keeps the agent generic and makes the Terraform repository the source of truth for infrastructure.

## Backend and variables

The real implementation uses an Azure Storage backend and environment-specific variable files. Those values are intentionally excluded from this portfolio repository.
