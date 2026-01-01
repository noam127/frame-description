"""Custom exceptions for the video frame description tool."""


class FrameDescriptionError(Exception):
    """Base exception for all frame description errors."""
    pass


# Video processing errors
class VideoNotFoundError(FrameDescriptionError):
    """Raised when the video file is not found."""
    pass


class InvalidVideoFormatError(FrameDescriptionError):
    """Raised when the video format is invalid or cannot be read."""
    pass


class TimestampOutOfBoundsError(FrameDescriptionError):
    """Raised when the timestamp exceeds the video duration."""
    pass


class FrameExtractionError(FrameDescriptionError):
    """Raised when frame extraction fails."""
    pass


# API errors
class APIConnectionError(FrameDescriptionError):
    """Raised when connection to the API fails."""
    pass


class APITimeoutError(FrameDescriptionError):
    """Raised when the API request times out."""
    pass


class APIRateLimitError(FrameDescriptionError):
    """Raised when API rate limit is exceeded."""
    pass


class APIResponseError(FrameDescriptionError):
    """Raised when the API returns an unexpected response."""
    pass


class JSONParseError(FrameDescriptionError):
    """Raised when JSON parsing fails."""
    pass


# Database errors
class ConnectionFailureError(FrameDescriptionError):
    """Raised when database connection fails."""
    pass


class DuplicateFrameError(FrameDescriptionError):
    """Raised when trying to insert a duplicate frame description."""
    pass


class DatabaseWriteError(FrameDescriptionError):
    """Raised when database write operation fails."""
    pass


# Configuration errors
class ConfigurationError(FrameDescriptionError):
    """Raised when configuration is invalid or missing."""
    pass
