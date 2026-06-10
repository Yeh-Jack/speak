import pytest
from app.services.chunking_service import ChunkingService, ChunkingConfig, VideoChunk
from app.services.exceptions import ChunkingError


@pytest.fixture
def chunking_service():
    return ChunkingService()


@pytest.fixture
def sample_transcript():
    return [
        {"start": 0.0, "end": 5.0, "text": "Welcome to this video."},
        {"start": 5.0, "end": 10.0, "text": "Today we will learn about Python."},
        {"start": 10.0, "end": 15.0, "text": "Let's start with variables!"},
        {"start": 15.0, "end": 20.0, "text": "Variables store data."},
        {"start": 20.0, "end": 25.0, "text": "There are many types."},
        {"start": 25.0, "end": 30.0, "text": "Strings, numbers, and booleans."},
        {
            "start": 30.0,
            "end": 35.0,
            "text": "This is a longer sentence that might need more context.",
        },
        {"start": 35.0, "end": 40.0, "text": "Let's continue learning."},
    ]


def test_chunking_service_initialization(chunking_service):
    """ChunkingService should have default search window of 30s."""
    assert chunking_service.SEARCH_WINDOW == 30.0
    assert chunking_service.SENTENCE_PUNCTUATION == {".", "!", "?"}


def test_ends_with_sentence_punctuation(chunking_service):
    """_ends_with_sentence should detect sentence endings."""
    assert chunking_service._ends_with_sentence("Hello world.") is True
    assert chunking_service._ends_with_sentence("What?") is True
    assert chunking_service._ends_with_sentence("Stop!") is True
    assert chunking_service._ends_with_sentence("no period") is False
    assert chunking_service._ends_with_sentence("") is False


def test_find_sentence_boundary_in_window(chunking_service, sample_transcript):
    """Should find sentence boundary within ±30s window."""
    boundary = chunking_service._find_sentence_boundary(
        25.0, sample_transcript, chunk_start=0.0, video_duration=40.0
    )
    assert boundary == 25.0


def test_find_sentence_boundary_no_boundary_in_window(chunking_service):
    """Should return target time if no boundary in window."""
    transcript = [
        {"start": 0.0, "end": 5.0, "text": "No period here"},
        {"start": 5.0, "end": 10.0, "text": "Still no period"},
    ]
    boundary = chunking_service._find_sentence_boundary(
        25.0, transcript, chunk_start=0.0, video_duration=40.0
    )
    assert boundary == 25.0


@pytest.mark.asyncio
async def test_create_chunks_hybrid_dynamic(chunking_service, sample_transcript):
    """Should create chunks with Hybrid Dynamic sentence-snap."""
    chunks = await chunking_service.create_chunks(
        video_duration=40.0, transcript=sample_transcript, chunk_duration=15.0
    )
    assert len(chunks) == 4
    assert chunks[0].start_time == 0.0
    assert chunks[0].end_time == 15.0
    assert chunks[0].index == 0
    assert chunks[1].start_time == 15.0
    assert chunks[1].end_time == 30.0
    assert chunks[1].index == 1
    assert chunks[2].start_time == 30.0
    assert chunks[2].end_time == 35.0
    assert chunks[2].index == 2
    assert chunks[3].start_time == 35.0
    assert chunks[3].end_time == 40.0
    assert chunks[3].index == 3


@pytest.mark.asyncio
async def test_create_chunks_respects_chunk_duration(chunking_service, sample_transcript):
    """Chunk duration should be user-adjustable."""
    chunks = await chunking_service.create_chunks(
        video_duration=40.0, transcript=sample_transcript, chunk_duration=20.0
    )
    assert len(chunks) == 3
    assert chunks[0].duration == 20.0
    assert chunks[1].duration == 15.0
    assert chunks[2].duration == 5.0


@pytest.mark.asyncio
async def test_create_chunks_snaps_to_misaligned_sentence(chunking_service):
    """Should snap to sentence when it's within ±30s but not at ideal boundary."""
    transcript = [
        {"start": 0.0, "end": 5.0, "text": "Hello world."},
        {"start": 5.0, "end": 12.0, "text": "This sentence ends at 12 seconds!"},
        {"start": 12.0, "end": 20.0, "text": "Another sentence here."},
        {"start": 20.0, "end": 30.0, "text": "Final sentence."},
    ]
    chunks = await chunking_service.create_chunks(
        video_duration=30.0, transcript=transcript, chunk_duration=15.0
    )
    assert len(chunks) == 3
    assert chunks[0].start_time == 0.0
    assert chunks[0].end_time == 12.0
    assert chunks[1].start_time == 12.0
    assert chunks[1].end_time == 20.0
    assert chunks[2].start_time == 20.0
    assert chunks[2].end_time == 30.0


class TestChunkingConfig:
    """Tests for ChunkingConfig dataclass."""

    def test_chunking_config_defaults(self):
        """ChunkingConfig should have correct default values."""
        config = ChunkingConfig()
        assert config.default_duration == 300
        assert config.min_duration == 60
        assert config.max_duration == 600
        assert config.search_window == 30.0

    def test_chunking_config_custom_values(self):
        """ChunkingConfig should accept custom values."""
        config = ChunkingConfig(
            default_duration=600,
            min_duration=120,
            max_duration=900,
            search_window=45.0,
        )
        assert config.default_duration == 600
        assert config.min_duration == 120
        assert config.max_duration == 900
        assert config.search_window == 45.0


class TestVideoChunk:
    """Tests for VideoChunk dataclass."""

    def test_video_chunk_creation(self):
        """VideoChunk should store chunk data correctly."""
        chunk = VideoChunk(
            index=0,
            start_time=0.0,
            end_time=300.0,
            duration=300.0,
        )
        assert chunk.index == 0
        assert chunk.start_time == 0.0
        assert chunk.end_time == 300.0
        assert chunk.duration == 300.0

    def test_video_chunk_duration_calculation(self):
        """VideoChunk duration should be end - start."""
        chunk = VideoChunk(
            index=1,
            start_time=300.0,
            end_time=600.0,
            duration=300.0,
        )
        assert chunk.duration == chunk.end_time - chunk.start_time


class TestCreateChunksEdgeCases:
    """Tests for edge cases in create_chunks."""

    @pytest.mark.asyncio
    async def test_create_chunks_invalid_duration_raises_error(self, chunking_service):
        """create_chunks should raise ChunkingError for invalid duration."""
        with pytest.raises(ChunkingError) as exc_info:
            await chunking_service.create_chunks(
                video_duration=-1.0, transcript=[]
            )
        assert "Invalid video duration" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_chunks_zero_duration_raises_error(self, chunking_service):
        """create_chunks should raise ChunkingError for zero duration."""
        with pytest.raises(ChunkingError) as exc_info:
            await chunking_service.create_chunks(
                video_duration=0.0, transcript=[]
            )
        assert "Invalid video duration" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_chunks_empty_transcript_uses_ideal_chunks(self, chunking_service):
        """create_chunks should use ideal chunks when transcript is empty."""
        chunks = await chunking_service.create_chunks(
            video_duration=60.0, transcript=[], chunk_duration=30.0
        )
        assert len(chunks) == 2
        assert chunks[0].start_time == 0.0
        assert chunks[0].end_time == 30.0
        assert chunks[1].start_time == 30.0
        assert chunks[1].end_time == 60.0

    @pytest.mark.asyncio
    async def test_create_ideal_chunks_exact_duration(self, chunking_service):
        """_create_ideal_chunks should create correct chunk count."""
        chunks = await chunking_service.create_chunks(
            video_duration=90.0, transcript=[], chunk_duration=30.0
        )
        assert len(chunks) == 3
        assert all(c.duration == 30.0 for c in chunks)

    @pytest.mark.asyncio
    async def test_create_chunks_last_chunk_shorter(self, chunking_service):
        """Last chunk should be shorter if video doesn't divide evenly."""
        chunks = await chunking_service.create_chunks(
            video_duration=70.0, transcript=[], chunk_duration=30.0
        )
        assert len(chunks) == 3
        assert chunks[0].duration == 30.0
        assert chunks[1].duration == 30.0
        assert chunks[2].duration == 10.0

    @pytest.mark.asyncio
    async def test_create_chunks_uses_custom_config(self):
        """create_chunks should use custom ChunkingConfig."""
        config = ChunkingConfig(default_duration=60)
        service = ChunkingService(config=config)
        chunks = await service.create_chunks(
            video_duration=60.0, transcript=[]
        )
        assert len(chunks) == 1
        assert chunks[0].duration == 60.0

    def test_find_sentence_boundary_last_chunk(self, chunking_service):
        """_find_sentence_boundary should find boundary for last chunk."""
        transcript = [
            {"start": 0.0, "end": 5.0, "text": "Hello world."},
            {"start": 5.0, "end": 10.0, "text": "This is a test."},
        ]
        boundary = chunking_service._find_sentence_boundary(
            10.0, transcript, chunk_start=0.0, video_duration=10.0
        )
        assert boundary == 5.0

    def test_find_sentence_boundary_limits_search(self, chunking_service):
        """_find_sentence_boundary should not search before chunk_start."""
        transcript = [
            {"start": 0.0, "end": 5.0, "text": "Old sentence."},
            {"start": 25.0, "end": 30.0, "text": "New sentence."},
        ]
        boundary = chunking_service._find_sentence_boundary(
            25.0, transcript, chunk_start=20.0, video_duration=60.0
        )
        assert boundary == 25.0
