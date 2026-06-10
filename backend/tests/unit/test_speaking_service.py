"""Tests for SpeakingService."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.speaking_service import SpeakingService


@pytest.fixture
def speaking_service(tmp_path):
    """Create SpeakingService with temp directory."""
    return SpeakingService(storage_dir=tmp_path)


class TestSpeakingServiceInitialization:
    """Tests for SpeakingService initialization."""

    def test_initialization_creates_recordings_dir(self, tmp_path):
        """SpeakingService should create recordings directory."""
        service = SpeakingService(storage_dir=tmp_path)
        assert service.recordings_dir == tmp_path / "recordings"
        assert service.recordings_dir.exists()


class TestCalculateSimilarity:
    """Tests for calculate_similarity method."""

    def test_calculate_similarity_full_match(self, speaking_service):
        """Full word match should return 1.0."""
        result = speaking_service.calculate_similarity(
            "hello world", "hello world"
        )
        assert result == 1.0

    def test_calculate_similarity_partial_match(self, speaking_service):
        """Partial word match should return proportion."""
        result = speaking_service.calculate_similarity(
            "hello world foo bar", "hello world baz qux"
        )
        expected = 2 / 6
        assert result == pytest.approx(expected)

    def test_calculate_similarity_no_match(self, speaking_service):
        """No common words should return 0.0."""
        result = speaking_service.calculate_similarity(
            "hello world", "foo bar"
        )
        assert result == 0.0

    def test_calculate_similarity_empty_original(self, speaking_service):
        """Empty original text should return 0.0."""
        result = speaking_service.calculate_similarity("", "hello world")
        assert result == 0.0

    def test_calculate_similarity_empty_user(self, speaking_service):
        """Empty user text should return 0.0."""
        result = speaking_service.calculate_similarity("hello world", "")
        assert result == 0.0

    def test_calculate_similarity_case_insensitive(self, speaking_service):
        """Comparison should be case insensitive."""
        result = speaking_service.calculate_similarity(
            "HELLO WORLD", "hello world"
        )
        assert result == 1.0


class TestGenerateFeedback:
    """Tests for _generate_feedback method."""

    def test_feedback_excellent(self, speaking_service):
        """High similarity (>= 0.8) should give excellent feedback."""
        feedback = speaking_service._generate_feedback(
            "hello world", "hello world", 0.85
        )
        assert "Excellent" in feedback

    def test_feedback_good(self, speaking_service):
        """Medium-high similarity (>= 0.6, < 0.8) should give good feedback."""
        feedback = speaking_service._generate_feedback(
            "hello world", "hello world test", 0.65
        )
        assert "Good" in feedback

    def test_feedback_nice_try(self, speaking_service):
        """Medium similarity (>= 0.4, < 0.6) should give nice try feedback."""
        feedback = speaking_service._generate_feedback(
            "hello world", "hello", 0.45
        )
        assert "Nice try" in feedback

    def test_feedback_keep_practicing(self, speaking_service):
        """Low similarity (< 0.4) should give keep practicing feedback."""
        feedback = speaking_service._generate_feedback(
            "hello world", "foo bar", 0.2
        )
        assert "Keep practicing" in feedback


class TestSaveRecording:
    """Tests for save_recording method."""

    @pytest.mark.asyncio
    async def test_save_recording_creates_file(self, speaking_service, tmp_path):
        """save_recording should create file with audio data."""
        audio_data = b"fake audio data"
        video_id = "test-video-id"
        segment_start = 10.0

        result = await speaking_service.save_recording(
            audio_data, video_id, segment_start
        )

        assert result.exists()
        assert result.name == f"{video_id}_{segment_start}.webm"
        assert result.read_bytes() == audio_data

    @pytest.mark.asyncio
    async def test_save_recording_creates_parent_dir(self, speaking_service, tmp_path):
        """save_recording should create parent directories if needed."""
        audio_data = b"fake audio data"
        nested_video_id = "nested/video/id"
        segment_start = 0.0

        result = await speaking_service.save_recording(
            audio_data, nested_video_id, segment_start
        )

        assert result.exists()


class TestExtractAudioSegment:
    """Tests for extract_audio_segment method."""

    @pytest.mark.asyncio
    async def test_extract_audio_segment_ffmpeg_failure(self, speaking_service, tmp_path):
        """extract_audio_segment should raise ValueError on FFmpeg failure."""
        video_path = tmp_path / "video.webm"
        video_path.touch()

        with patch(
            "app.services.speaking_service.asyncio.create_subprocess_exec"
        ) as mock_exec:
            mock_process = MagicMock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(
                return_value=(b"", b"FFmpeg error: invalid input")
            )
            mock_exec.return_value = mock_process

            with pytest.raises(ValueError) as exc_info:
                await speaking_service.extract_audio_segment(
                    video_path, 0.0, 5.0
                )
            assert "FFmpeg audio extraction failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_audio_segment_custom_output_path(self, speaking_service, tmp_path):
        """extract_audio_segment should use custom output path if provided."""
        video_path = tmp_path / "video.webm"
        video_path.touch()
        output_path = tmp_path / "custom_output.wav"

        with patch(
            "app.services.speaking_service.asyncio.create_subprocess_exec"
        ) as mock_exec:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process

            result = await speaking_service.extract_audio_segment(
                video_path, 0.0, 5.0, output_path=output_path
            )

            assert result == output_path


class TestCompareRecordings:
    """Tests for compare_recordings method."""

    @pytest.mark.asyncio
    async def test_compare_recordings_similarity_calculation(self, speaking_service, tmp_path):
        """compare_recordings should calculate similarity between transcriptions."""
        original_path = tmp_path / "original.wav"
        user_path = tmp_path / "user.wav"

        with patch.object(
            speaking_service, "transcribe_audio", new_callable=AsyncMock
        ) as mock_transcribe:
            mock_transcribe.side_effect = ["hello world test", "hello world test"]

            with patch.object(
                speaking_service, "calculate_similarity", return_value=1.0
            ):
                result = await speaking_service.compare_recordings(
                    original_path, user_path
                )

            assert result["original_text"] == "hello world test"
            assert result["user_text"] == "hello world test"
            assert result["similarity_score"] == 1.0
            assert "Excellent" in result["feedback"]