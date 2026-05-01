# =============================================================================
# Base image — purpose: match project Python requirement (>=3.12) with a small OS.
# --------------------------------------------------------------------------------
FROM python:3.12-slim

# -----------------------------------------------------------------------------
# System packages — purpose: git must be present; gitkit runs `git` via subprocess.
# Install only what's needed and clear apt lists to keep the layer small.
# -----------------------------------------------------------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Environment — purpose:
# PYTHONUNBUFFERED=1 → logs/prints show immediately (no buffering in containers).
# PYTHONDONTWRITEBYTECODE=1 → avoids writing .pyc files into image layers.
# -----------------------------------------------------------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# -----------------------------------------------------------------------------
# Working directory — purpose:
# Expected use: bind-mount your repo here, e.g. `docker run -v "$(pwd):/workspace" …`
# so clean-branches, stats, sync-fork operate on that repository.
# -----------------------------------------------------------------------------
WORKDIR /workspace

# -----------------------------------------------------------------------------
# Project files — purpose: copy only what's required to install the package
# (matches setuptools layout: pyproject.toml, README, packages under src/).
# -----------------------------------------------------------------------------
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# -----------------------------------------------------------------------------
# Install gitkit — purpose: install runtime deps (click, rich) from pyproject.toml.
# Omit optional [dev] so the image stays lean for end users / CI parity with wheel.
# -----------------------------------------------------------------------------
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

# -----------------------------------------------------------------------------
# Git safety for bind mounts — purpose:
# Mark /workspace as trusted to avoid "detected dubious ownership" when host
# repositories are mounted from Windows/macOS into the Linux container.
# -----------------------------------------------------------------------------
RUN git config --system --add safe.directory /workspace

# -----------------------------------------------------------------------------
# Non-root user — purpose: safer default than running as root when operating on mounts.
# UID 1000 often matches host user for writable bind mounts without root on files.
# -----------------------------------------------------------------------------
RUN useradd --create-home --uid 1000 gitkit \
    && chown -R gitkit:gitkit /workspace

USER gitkit

# ----------------------------------------------------------------------------
# Entry point — purpose: `[project.scripts] gitkit` is the CLI; args become subcommands.
# Default CMD shows help; override e.g. `docker run IMAGE stats HEAD --json`.
# -----------------------------------------------------------------------------
ENTRYPOINT ["gitkit"]
CMD ["--help"]
