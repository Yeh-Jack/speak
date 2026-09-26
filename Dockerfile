# This Dockerfile builds a Docker image for the Speak application within two
# stages which reduces the image size from 37.8GB to 18.4GB.
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
# The base image also includes CUDA 12.8 which is required for native Blackwell compilation.
# Use 'devel' variant to get the CUDA compiler and libraries for building llama-cpp-python with CUDA support.
# ============================================================
FROM nvidia/cuda:12.8.1-devel-ubuntu24.04 AS builder

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
    CUDA_HOME=/usr/local/cuda \
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

# llama-cpp-python is compiled against CUDA 12.8.
#
# 60  = NVIDIA Pascal / Tesla P100
# 120 = NVIDIA Blackwell / RTX 5090
#
# GGLM_NATIVE=OFF avoids compiling for the build host CPU only.
ENV CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=60;120" \
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
# Use cuDNN runtime because faster-whisper / CTranslate2 speech
# workloads can require cuDNN.
# ============================================================
FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04 AS runtime

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
    CUDA_HOME=/usr/local/cuda \
    PATH="${UV_PROJECT_ENVIRONMENT}/bin:${PATH}"

# Runtime-only system packages.
# libssl3t64 is OpenSSL 3.1.2 library which is required by llama-cpp-python >= 0.1.80.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        ffmpeg \
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
# Don't try to initialize CUDA here:
# libcuda.so.1 comes from the NVIDIA host driver and is normally
# injected when the container is started with --gpus.
# ------------------------------------------------------------
RUN python3.12 --version && \
    python3.12 -c "import importlib.metadata as m; \
print('llama-cpp-python:', m.version('llama-cpp-python')); \
print('ctranslate2:', m.version('ctranslate2')); \
print('faster-whisper:', m.version('faster-whisper')); \
print('pyannote.audio:', m.version('pyannote.audio')); \
print('yt-dlp:', m.version('yt-dlp'))" && \
    ffmpeg -version | head -n 1 && \
    python3.12 -c "import importlib.metadata; print('llama-cpp-python:', importlib.metadata.version('llama-cpp-python'))"

# Expose port
EXPOSE 8080

# Default command
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
