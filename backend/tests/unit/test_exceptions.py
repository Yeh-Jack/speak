import pytest
from app.services.exceptions import (
    VideoProcessingError,
    DownloadError,
    ChunkingError,
    TranscriptionError,
    StudyPlanError,
)


def test_video_processing_error_has_checkpoint():
    """VideoProcessingError should store checkpoint state."""
    error = VideoProcessingError("test", checkpoint_state="downloading", failed_step="download")
    assert error.checkpoint_state == "downloading"
    assert error.failed_step == "download"
    assert "test" in str(error)


def test_specific_exceptions_inherit():
    """All specific exceptions should inherit from VideoProcessingError."""
    assert issubclass(DownloadError, VideoProcessingError)
    assert issubclass(ChunkingError, VideoProcessingError)
    assert issubclass(TranscriptionError, VideoProcessingError)
    assert issubclass(StudyPlanError, VideoProcessingError)


def test_download_error_message():
    """DownloadError should store message accessible via .message attribute."""
    error = DownloadError("network failed")
    assert error.message == "network failed"
    assert error.checkpoint_state == "downloading"
    assert error.failed_step == "download"


def test_chunking_error_message():
    """ChunkingError should store message accessible via .message attribute."""
    error = ChunkingError("chunking failed")
    assert error.message == "chunking failed"
    assert error.checkpoint_state == "chunking"
    assert error.failed_step == "chunking"


def test_transcription_error_message():
    """TranscriptionError should store message accessible via .message attribute."""
    error = TranscriptionError("transcription failed")
    assert error.message == "transcription failed"
    assert error.checkpoint_state == "transcribing"
    assert error.failed_step == "transcription"


def test_study_plan_error_message():
    """StudyPlanError should store message accessible via .message attribute."""
    error = StudyPlanError("study plan failed")
    assert error.message == "study plan failed"
    assert error.checkpoint_state == "studying"
    assert error.failed_step == "study_plan"
