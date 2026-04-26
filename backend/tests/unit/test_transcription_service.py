import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

from app.services.transcription_service import TranscriptionService, SubtitleService
from app.services.exceptions import TranscriptionError


@pytest.fixture
def transcription_service(tmp_path):
    return TranscriptionService(storage_dir=tmp_path)


def test_subtitle_service_parses_srt():
    """SubtitleService should parse SRT format."""
    import tempfile

    service = SubtitleService()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False) as f:
        f.write("1\n00:00:00,000 --> 00:00:05,000\nHello world.\n")
        f.flush()

        entries = service.parse_subtitle_file(Path(f.name))

        assert len(entries) == 1
        assert entries[0]["text"] == "Hello world."
        assert entries[0]["start"] == 0.0
        assert entries[0]["end"] == 5.0


def test_subtitle_service_extracts_speaker():
    """SubtitleService should extract speaker labels."""
    import tempfile

    service = SubtitleService()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False) as f:
        f.write("1\n00:00:00,000 --> 00:00:05,000\nJohn: Hello there.\n")
        f.flush()

        entries = service.parse_subtitle_file(Path(f.name))

        assert entries[0]["speaker"] == "John"


@pytest.mark.asyncio
async def test_transcription_service_youtube_strategy_first(transcription_service, tmp_path):
    """TranscriptionService should try YouTube subtitles first."""
    video_path = tmp_path / "video.webm"
    video_path.touch()

    mock_transcript = [{"start": 0.0, "end": 5.0, "text": "Test sentence.", "speaker": None}]

    with patch.object(
        transcription_service, "_try_youtube_subtitles", new_callable=AsyncMock
    ) as mock_yt:
        mock_yt.return_value = mock_transcript

        result = await transcription_service.transcribe(video_path)

        assert result == mock_transcript
        mock_yt.assert_called_once()


@pytest.mark.asyncio
async def test_transcription_service_fallback_to_whisper(transcription_service, tmp_path):
    """TranscriptionService should fallback to Whisper if YouTube fails."""
    video_path = tmp_path / "video.webm"
    video_path.touch()

    mock_transcript = [
        {"start": 0.0, "end": 5.0, "text": "Whisper transcription.", "speaker": None}
    ]

    with patch.object(
        transcription_service, "_try_youtube_subtitles", new_callable=AsyncMock
    ) as mock_yt:
        mock_yt.return_value = None

        with patch.object(
            transcription_service, "_transcribe_with_whisper", new_callable=AsyncMock
        ) as mock_whisper:
            mock_whisper.return_value = mock_transcript

            result = await transcription_service.transcribe(video_path)

            assert result == mock_transcript
            mock_whisper.assert_called_once()


@pytest.mark.asyncio
async def test_transcription_service_raises_error_on_complete_failure(
    transcription_service, tmp_path
):
    """TranscriptionService should raise TranscriptionError if all methods fail."""
    video_path = tmp_path / "video.webm"
    video_path.touch()

    with patch.object(
        transcription_service, "_try_youtube_subtitles", new_callable=AsyncMock
    ) as mock_yt:
        mock_yt.return_value = None

        with patch.object(
            transcription_service, "_transcribe_with_whisper", new_callable=AsyncMock
        ) as mock_whisper:
            mock_whisper.side_effect = Exception("Whisper failed")

            with pytest.raises(TranscriptionError) as exc_info:
                await transcription_service.transcribe(video_path)

            assert "Failed to transcribe video" in str(exc_info.value)
