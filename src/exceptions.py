class FrameDescriptionError(Exception):
    """Base exception for all frame description errors."""
    pass


# Video Processing Errors
class VideoProcessingError(FrameDescriptionError):
    pass


class VideoNotFoundError(VideoProcessingError):
    pass


class InvalidVideoFormatError(VideoProcessingError):
    pass


class TimestampOutOfBoundsError(VideoProcessingError):
    pass


class FrameExtractionError(VideoProcessingError):
    pass


# Anthropic API errors
class AnthropicAPIError(FrameDescriptionError):
    pass


class APIConnectionError(AnthropicAPIError):
    pass


class APITimeoutError(AnthropicAPIError):
    pass


class APIRateLimitError(AnthropicAPIError):
    pass


class APIBadResponseError(AnthropicAPIError):
    pass


class JSONParseError(AnthropicAPIError):
    pass


# Database errors
class DatabaseError(FrameDescriptionError):
    pass


class DatabaseConnectionFailureError(DatabaseError):
    pass


class DatabaseDuplicateEntryError(DatabaseError):
    pass


class DatabaseWriteError(DatabaseError):
    pass


# Configuration errors
class ConfigurationError(FrameDescriptionError):
    pass
