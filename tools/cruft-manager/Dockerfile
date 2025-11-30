# Cruft Manager Container
# Runs cruft template updates on a schedule
#
# SPDX-FileCopyrightText: 2025 Byron Williams
# SPDX-License-Identifier: MIT

FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/ByronWilliamsCPA/homelab_infra"
LABEL org.opencontainers.image.description="Cruft template update manager"
LABEL org.opencontainers.image.licenses="MIT"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir cruft pyyaml

# Create non-root user
RUN useradd -m -s /bin/bash cruft-manager
USER cruft-manager
WORKDIR /home/cruft-manager

# Configure git
RUN git config --global user.name "cruft-manager[bot]" \
    && git config --global user.email "cruft-manager@homelab.local"

# Copy application
COPY --chown=cruft-manager:cruft-manager cruft_manager.py .
COPY --chown=cruft-manager:cruft-manager cruft_registry.yaml .

# Default command - dry run check
CMD ["python", "cruft_manager.py", "--dry-run", "--verbose"]
