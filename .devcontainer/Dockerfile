FROM mcr.microsoft.com/devcontainers/python:3-3.14-trixie

# Switch to root to install packages
USER root

# Install xdg-utils, Node.js (latest LTS via NodeSource), npm, and the AWS AgentCore CLI
# Running this as a single RUN command ensures optimal Docker layer caching
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y xdg-utils ca-certificates curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @aws/agentcore \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN pip install uv

# Switch back to the non-root user that VS Code expects
USER vscode