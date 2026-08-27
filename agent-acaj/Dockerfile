FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        unzip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# Terraform
ARG TERRAFORM_VERSION=1.13.2

RUN curl -fsSLo /tmp/terraform.zip \
        "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" \
    && unzip /tmp/terraform.zip -d /usr/local/bin \
    && rm /tmp/terraform.zip

# Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# IMPORTANT:
# Copy both the orchestration file AND the tools module.
COPY main.py .
COPY deploy_agent.py .
COPY deploy_agent_tools.py .

# Optional sanity checks during image build
RUN python --version \
    && python -c "import deploy_agent_tools; print('deploy_agent_tools: OK')" \
    && terraform version \
    && az version \
    && gh --version \
    && git --version

CMD ["python", "main.py"]