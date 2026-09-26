# This Dockerfile builds a Docker image for the Speak application in one stage which resulting in a 37.8GB image.
#
# Ubuntu 24.04 provides Python 3.12 which is required for llama-cpp-python >= 0.1.80.
# The base image also includes CUDA 12.8 which is required for native Blackwell compilation.
# Use 'devel' variant to get the CUDA compiler and libraries for building llama-cpp-python with CUDA support.
FROM nvidia/cuda:12.8.1-devel-ubuntu24.04

# ---------------------------------------------------------------------------
# Default configurations for this application
# ---------------------------------------------------------------------------
ARG APP_DIR=/app
ARG BACKEND=backend
ARG FRONTEND=frontend
ARG BACK_DIR=${APP_DIR}/${BACKEND}
ARG FRONT_DIR=${APP_DIR}/${FRONTEND}
ARG DATA_DIR=${APP_DIR}/data
ENV PROJECT_ROOT=${APP_DIR}

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    CUDA_HOME=/usr/local/cuda \
    PATH="/opt/venv/bin:${PATH}"

# ---------------------------------------------------------------------------
# Install uv
# ---------------------------------------------------------------------------
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /usr/local/bin/

# ---------------------------------------------------------------------------
# System packages
# ---------------------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-dev \
        python3.12-venv \
        build-essential \
        cmake \
        ninja-build \
        ca-certificates \
        curl \
        git \
        ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    # Create an isolat ed Python 3.12 environment.
    uv venv --python python3.12 /opt/venv && \
    # Create data directories for audio, SQLite, models, subtitles, transcripts and videos.
    mkdir -p ${DATA_DIR}/audio && \
    mkdir -p ${DATA_DIR}/db && \
    mkdir -p ${DATA_DIR}/models && \
    mkdir -p ${DATA_DIR}/subtitles && \
    mkdir -p ${DATA_DIR}/transcripts && \
    mkdir -p ${DATA_DIR}/videos && \
    # Create application directories for backend and frontend.
    mkdir -p ${BACK_DIR} ${FRONT_DIR}

# ---------------------------------------------------------------------------
# Build llama-cpp-python with CUDA
#
# Tesla P100 = SM 60
# RTX5090 = SM 120
# ---------------------------------------------------------------------------
ENV CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=60;120" \
    FORCE_CMAKE=1
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/venv \
        --upgrade \
        --no-cache-dir \
        llama-cpp-python

# ---------------------------------------------------------------------------
# yt-dlp
# ---------------------------------------------------------------------------
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/venv \
        --upgrade \
        "yt-dlp[default]"

# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
RUN python --version && \
    uv --version && \
    ffmpeg -version | head -n 1 && \
    yt-dlp --version && \
    python -c "import importlib.metadata; print('llama-cpp-python:', importlib.metadata.version('llama-cpp-python'))"

# ---------------------------------------------------------------------------
# Install application dependencies and copy application code
# ---------------------------------------------------------------------------
WORKDIR ${BACK_DIR}

# Copy dependency files
COPY ${BACKEND}/pyproject.toml ${BACKEND}/uv.lock ${BACKEND}/README.md ./

# Install dependencies using uv
RUN uv sync

# Copy application code
# COPY alembic.ini ./
COPY ${BACKEND}/app ${BACK_DIR}/app
COPY ${BACKEND}/alembic ${BACK_DIR}/alembic
COPY ${BACKEND}/scripts ${BACK_DIR}/scripts
COPY ${BACKEND}/.env.example ${DATA_DIR}/env.example
COPY ${FRONTEND}/dist ${FRONT_DIR}/dist

# Expose port
EXPOSE 8080

# Default command
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
