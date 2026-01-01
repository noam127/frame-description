import os
import cv2
from typing import Tuple
from .exceptions import (
    VideoNotFoundError,
    InvalidVideoFormatError,
    TimestampOutOfBoundsError,
    FrameExtractionError
)


def extract_frame(video_path: str, timestamp: float) -> Tuple[bytes, dict]:
    """Extract a frame from a video at the specified timestamp.

    Returns:
        A tuple of (frame_bytes, metadata) where
        - frame_bytes: JPEG-encoded frame as bytes
        - metadata: Dictionary with video and frame metadata
    """
    # Validate video file exists
    if not os.path.exists(video_path):
        raise VideoNotFoundError(f"Video file not found: {video_path}")

    # Open video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise InvalidVideoFormatError(
            f"Cannot open video file: {video_path}. "
            "The file may be corrupted or in an unsupported format."
        )

    # Get video metadata
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    # Validate timestamp
    if timestamp < 0:
        raise TimestampOutOfBoundsError(f"Timestamp must be positive. Got: {timestamp}s")

    if timestamp > duration:
        raise TimestampOutOfBoundsError(f"Timestamp {timestamp}s exceeds video duration of {duration:.2f}s")

    # Seek to the timestamp (convert seconds to milliseconds)
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)

    # Read the frame and release the capture
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise FrameExtractionError(f"Failed to extract frame at timestamp {timestamp}s")

    # Convert frame to JPEG bytes
    success, buffer = cv2.imencode('.jpg', frame)

    if not success:
        raise FrameExtractionError(f"Failed to encode frame at timestamp {timestamp}s as JPEG")

    frame_bytes = buffer.tobytes()
    metadata = {
        "video_filename": os.path.basename(video_path),
        "video_duration": duration,
        "video_fps": fps,
        "frame_number": int(timestamp * fps),
        "frame_dimensions": {
            "width": width,
            "height": height
        }
    }

    return frame_bytes, metadata
