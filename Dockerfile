# =============================================================================
# Production image for gitkit (CLI). Intended for GHCR and local Docker use.
#
# Local build:
#   docker build -t gitkit:local .
#
# GitHub Actions builds from the same Dockerfile and pushes to ghcr.io.
# Optional build args improve registry metadata (passed by CI when set):
#   --build-arg GITKIT_VERSION=0.1.0
#   --build-arg GITKIT_REVISION=<git-sha>
# =============================================================================

FROM python:3.12-slim

# Optional metadata for GitHub Container Registry / OCI consumers.
ARG GITKIT_VERSION=0.1.0
ARG GITKIT_REVISION=local
ARG GITKIT_SOURCE_URL=https://github.com/ChandupaWijesinghe1/gitkit

LABEL org.opencontainers.image.title="gitkit"
LABEL org.opencontainers.image.description="CLI tool for Git branch cleanup, repository stats, and fork sync workflows"
LABEL org.opencontainers.image.version="${GITKIT_VERSION}"
LABEL org.opencontainers.image.revision="${GITKIT_REVISION}"
LABEL org.opencontainers.image.source="${GITKIT_SOURCE_URL}"
LABEL org.opencontainers.image.licenses="MIT"

# -----------------------------------------------------------------------------
# Git — gitkit shells out to `git` for all commands.
# -----------------------------------------------------------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Python / pip defaults for small, predictable containers.
# -----------------------------------------------------------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /workspace

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# -----------------------------------------------------------------------------
# Install app (runtime deps only — no dev tools in the published image).
# -----------------------------------------------------------------------------
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir .

# Allow Git operations on mounted host repos (avoids dubious ownership errors).
RUN git config --system --add safe.directory /workspace

RUN useradd --create-home --uid 1000 gitkit \
    && chown -R gitkit:gitkit /workspace

USER gitkit

ENTRYPOINT ["gitkit"]
CMD ["--help"]
