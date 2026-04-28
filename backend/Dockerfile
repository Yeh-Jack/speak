FROM python:3.13-slim

RUN \
# Install system dependencies
    apt-get update && apt-get install -y curl ffmpeg gcc && \
    rm -rf /var/lib/apt/lists/* && \
# Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
# Create data directories for audio, courses, SQLite, models, transcripts and videos.
    mkdir -p /app/data/{audio,courses,db,models,transcripts,videos}

ENV PATH="/root/.cargo/bin:${PATH}"
ENV PROJECT_ROOT=/app
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/
COPY alembic.ini ./

# Expose port
EXPOSE 8080

# Default command
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
