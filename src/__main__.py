import sys
import argparse
import json
import os
from .config import load_config
from .video_processor import extract_frame
from .claude_client import describe_frame
from .database import FrameDescriptionRepository
from .exceptions import FrameDescriptionError, VideoProcessingError, AnthropicAPIError, DatabaseError, ConfigurationError


def parse_cli_args():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Extract a frame from a video, analyze it with Claude AI, and store in MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main video.mp4 45.5
  python -m src.main /path/to/video.mp4 45.5 --verbose
  python -m src.main video.mp4 45.5 --output-json
        """
    )

    parser.add_argument(
        "video_path",
        help="Path to the video file"
    )

    parser.add_argument(
        "timestamp",
        type=float,
        help="Timestamp in seconds where to extract the frame"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output result as JSON"
    )

    return parser.parse_args()


def execute_pipline(args):
    # Convert relative path to absolute path
    video_path = os.path.abspath(args.video_path)
    timestamp = args.timestamp

    # Load configuration
    if args.verbose and not args.output_json:
        print("Loading configuration...")
    config = load_config()

    # Extract frame
    if not args.output_json:
        print(f"Processing video: {video_path}")
        print(f"Extracting frame at timestamp: {timestamp}s")

    frame_bytes, frame_metadata = extract_frame(video_path, timestamp)

    if args.verbose and not args.output_json:
        print(f"Frame extracted successfully")
        print(f"  - Dimensions: {frame_metadata['frame_dimensions']['width']}x{frame_metadata['frame_dimensions']['height']}")
        print(f"  - Video FPS: {frame_metadata['video_fps']:.2f}")
        print(f"  - Video duration: {frame_metadata['video_duration']:.2f}s")

    # Analyze frame with Claude
    if not args.output_json:
        print("Analyzing frame with Claude API...")

    api_result = describe_frame(
        frame_bytes,
        config["anthropic_api_key"],
        config["claude_model"],
        config["max_tokens"]
    )

    if args.verbose and not args.output_json:
        print(f"Description received (tokens used: {api_result['tokens_used']})")

    # Store in MongoDB
    if not args.output_json:
        print("Storing results in MongoDB...")

    with FrameDescriptionRepository(
        config["mongodb_uri"],
        config["mongodb_database"],
        config["mongodb_collection"]
    ) as repo:
        # Build complete document
        document = {
            "video_path": video_path,
            "timestamp": timestamp,
            "description": api_result["description"],
            "frame_metadata": frame_metadata,
            "api_metadata": {
                "model": api_result["model"],
                "tokens_used": api_result["tokens_used"]
            }
        }

        document_id = repo.insert_description(document)

    return document_id, frame_metadata, api_result


def main():
    args = parse_cli_args()

    try:
        document_id, frame_metadata, api_result = execute_pipline(args)
        description = api_result["description"]

        if args.output_json:
            result = {
                "success": True,
                "document_id": document_id,
                "description": description,
                "frame_metadata": frame_metadata,
                "api_metadata": {
                    "model": api_result["model"],
                    "tokens_used": api_result["tokens_used"]
                }
            }

            print(json.dumps(result, indent=2))

        else:
            print(f"Success! Frame description stored with ID: {document_id}")
            print()
            print(f"Description: {description['scene']}")
            print(f"Objects detected: {', '.join(description['objects'])}")
            print(f"Setting: {description['setting']}")
            print(f"Time of day: {description['time_of_day']}")
            print(f"Weather: {description['weather']}")

        sys.exit(0)

    except Exception as e:
        is_frame_description_error = isinstance(e, FrameDescriptionError)
        exit_code = e.exit_code if is_frame_description_error else -1

        if args.output_json:
            error_string = str(e) if is_frame_description_error else f"Unexpected error: {str(e)}"
            print(json.dumps({"success": False, "error": error_string}))
        else:
            error_name = e.error_name if is_frame_description_error else "Unexpected Error"    
            print(f"{error_name}: {e}", file=sys.stderr)

        sys.exit(exit_code)


if __name__ == "__main__":
    main()
