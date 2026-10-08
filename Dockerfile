# This Dockerfile builds a CPU-only Docker image for the Speak application
# within two stages.
#
# The GPU variant lives in `Dockerfile-cuda`. Use that one when LLM inference
# should offload to an NVIDIA GPU; this image compiles llama-cpp-python without
# CUDA and carries no CUDA/cuDNN runtime, which keeps it much smaller.
#
# ---------------------------------------------------------------------------
# Default configurations for this application
# ---------------------------------------------------------------------------
ARG APP_DIR=/app
ARG BACKEND=backend
ARG FRONTEND=frontend
ARG BACK_DIR=${APP_DIR}/${BACKEND}
ARG FRONT_DIR=${APP_DIR}/${FRONTEND}
ARG DATA_DIR=${APP_DIR}/data
ARG UV_TARGET=/root/.cache/uv


# ============================================================
# Builder
#
# Ubuntu 24.04 provides Python 3.12 which is required for llama-cpp-python >= 0.1.80.
# Plain Ubuntu, no CUDA toolkit: llama-cpp-python builds its CPU backend here.
# ============================================================
FROM ubuntu:24.04 AS builder

ARG APP_DIR
ARG BACKEND
ARG BACK_DIR
ARG FRONTEND
ARG FRONT_DIR
ARG DATA_DIR
ARG UV_TARGET

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="${UV_PROJECT_ENVIRONMENT}/bin:${PATH}"

# Build dependencies only.
# libssl-dev is OpenSSL 3.1.2 development library which is required
# for building llama-cpp-python with SSL support.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-dev \
        python3.12-venv \
        build-essential \
        cmake \
        ca-certificates \
        curl \
        git \
        libssl-dev \
        ninja-build \
        pkg-config && \
    rm -rf /var/lib/apt/lists/* && \
    # Create data directories for audios, SQLite, models, subtitles, transcripts and videos.
    mkdir -p ${DATA_DIR}/audios && \
    mkdir -p ${DATA_DIR}/db && \
    mkdir -p ${DATA_DIR}/models && \
    mkdir -p ${DATA_DIR}/subtitles && \
    mkdir -p ${DATA_DIR}/transcripts && \
    mkdir -p ${DATA_DIR}/videos && \
    # Create application directories for backend and frontend.
    mkdir -p ${BACK_DIR} ${FRONT_DIR} && \
    mkdir -p ${UV_TARGET}

# Install pinned uv.
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /usr/local/bin/

WORKDIR ${BACK_DIR}

# ------------------------------------------------------------
# Python dependency installation
#
# Copy only dependency metadata first so Docker can cache this
# expensive layer when application source changes.
# ------------------------------------------------------------
COPY ${BACKEND}/pyproject.toml ${BACKEND}/uv.lock ${BACKEND}/README.md ./

# llama-cpp-python compiles the CPU backend only: GGML_CUDA=OFF leaves out
# the CUDA backend entirely so the build needs no nvcc.
#
# GGML_NATIVE=OFF keeps the build portable to any host CPU (no AVX/AVX2/NEON
# baked in). Set it to ON and rebuild on the target machine for peak speed.
ENV CMAKE_ARGS="-DGGML_CUDA=OFF -DGGML_NATIVE=OFF" \
    FORCE_CMAKE=1

RUN --mount=type=cache,target=${UV_TARGET} \
    uv sync \
        --frozen \
        --no-install-project \
        --no-dev

# ------------------------------------------------------------
# Application source (copy `alembic.ini` too for running DB migrations)
# ------------------------------------------------------------
# COPY alembic.ini ./
COPY ${BACKEND}/app ${BACK_DIR}/app
COPY ${BACKEND}/alembic ${BACK_DIR}/alembic
COPY ${BACKEND}/scripts ${BACK_DIR}/scripts
COPY ${BACKEND}/env.example ${DATA_DIR}/env.example
COPY ${FRONTEND}/dist ${FRONT_DIR}/dist

# Install the application itself.
#
# --no-editable means the runtime venv doesn't depend on the
# source tree being present at the same development location.
# ------------------------------------------------------------
RUN --mount=type=cache,target=${UV_TARGET} \
    uv sync \
        --frozen \
        --no-dev \
        --no-editable


# ============================================================
# Deno binary
# ============================================================
FROM denoland/deno:2.9.7 AS deno


# ============================================================
# Runtime
# ============================================================
#
# No CUDA runtime here: everything runs on the CPU.
# faster-whisper / CTranslate2 fall back to their CPU kernels automatically.
# ============================================================
FROM ubuntu:24.04 AS runtime

ARG APP_DIR
ARG BACKEND
ARG BACK_DIR
ARG FRONTEND
ARG FRONT_DIR
ARG DATA_DIR
ARG UV_TARGET

ENV PROJECT_ROOT=${APP_DIR}
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LLM_GPU_LAYERS=0 \
    PATH="${UV_PROJECT_ENVIRONMENT}/bin:${PATH}"

# Runtime-only system packages.
# libssl3t64 is OpenSSL 3.1.2 library which is required by llama-cpp-python >= 0.1.80.
# libgomp1 is the GCC OpenMP runtime which ggml and CTranslate2 link against.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        ffmpeg \
        libgomp1 \
        libssl3t64 \
        python3.12 && \
    rm -rf /var/lib/apt/lists/*

# Install pinned uv.
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /usr/local/bin/

# Install Deno: copy only the Deno executable from the official image.
COPY --from=deno /usr/bin/deno /usr/local/bin/deno

# ------------------------------------------------------------
# Python environment
# ------------------------------------------------------------
COPY --from=builder ${UV_PROJECT_ENVIRONMENT} ${UV_PROJECT_ENVIRONMENT}

# ------------------------------------------------------------
# Application
# ------------------------------------------------------------
COPY --from=builder ${APP_DIR} ${APP_DIR}
WORKDIR ${BACK_DIR}

# ------------------------------------------------------------
# Basic build-time verification
#
# Importing llama_cpp is the real check: it fails loudly when the ggml CPU
# backend did not link. llama_supports_gpu_offload() proves the CUDA backend
# was left out of the build.
# ------------------------------------------------------------
RUN python3.12 --version && \
    python3.12 -c "import importlib.metadata as m; \
print('llama-cpp-python:', m.version('llama-cpp-python')); \
print('ctranslate2:', m.version('ctranslate2')); \
print('faster-whisper:', m.version('faster-whisper')); \
print('yt-dlp:', m.version('yt-dlp'))" && \
    python3.12 -c "import llama_cpp; \
assert not llama_cpp.llama_supports_gpu_offload(), 'CUDA backend unexpectedly present'; \
print('llama-cpp-python: CPU-only backend confirmed')" && \
    ffmpeg -version | head -n 1

# Expose port
EXPOSE 8080

# Default command
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
