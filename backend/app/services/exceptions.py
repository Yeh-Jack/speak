"""Custom exceptions for video processing pipeline."""


class VideoProcessingError(Exception):
    """Base exception for video processing errors with checkpoint info."""

    def __init__(self, message: str, checkpoint_state: str, failed_step: str):
        self.message = message
        self.checkpoint_state = checkpoint_state
        self.failed_step = failed_step
        super().__init__(message)


class DownloadError(VideoProcessingError):
    """Raised when video download fails."""

    def __init__(self, message: str):
        super().__init__(message, checkpoint_state="downloading", failed_step="download")


class ChunkingError(VideoProcessingError):
    """Raised when video chunking fails."""

    def __init__(self, message: str):
        super().__init__(message, checkpoint_state="chunking", failed_step="chunking")


class TranscriptionError(VideoProcessingError):
    """Raised when transcription fails."""

    def __init__(self, message: str):
        super().__init__(message, checkpoint_state="transcribing", failed_step="transcription")


class StudyPlanError(VideoProcessingError):
    """Raised when study plan generation fails."""

    def __init__(self, message: str):
        super().__init__(message, checkpoint_state="studying", failed_step="study_plan")
