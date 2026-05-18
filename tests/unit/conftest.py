"""Pytest configuration for unit tests."""

import pytest
import asyncio
from pathlib import Path
import tempfile


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def tmp_path():
    """Create temporary path for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing chunking service."""
    return [
        {"start": 0.0, "end": 5.0, "text": "Welcome to this video."},
        {"start": 5.0, "end": 10.0, "text": "Today we will learn about Python."},
        {"start": 10.0, "end": 15.0, "text": "Let's start with variables!"},
        {"start": 15.0, "end": 20.0, "text": "Variables store data."},
        {"start": 20.0, "end": 25.0, "text": "There are many types."},
        {"start": 25.0, "end": 30.0, "text": "Strings, numbers, and booleans."},
        {"start": 30.0, "end": 35.0, "text": "This is a longer sentence."},
        {"start": 35.0, "end": 40.0, "text": "Let's continue learning."},
    ]
