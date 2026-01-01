class FrameDescriptionError(Exception):
    """Base exception for all frame description errors."""

    exit_code = None
    error_name = None


# Video Processing Errors
class VideoProcessingError(FrameDescriptionError):
    exit_code = 2
    error_name = "Video Processing Error"


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
    exit_code = 3
    error_name = "Anthropic API Error"


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
    exit_code = 4
    error_name = "Database Error"


class DatabaseConnectionFailureError(DatabaseError):
    pass


class DatabaseDuplicateEntryError(DatabaseError):
    pass


class DatabaseWriteError(DatabaseError):
    pass


# Configuration errors
class ConfigurationError(FrameDescriptionError):
    exit_code = 1
    error_name = "Configuration Error"
