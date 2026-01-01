# Video Frame Description Tool

A command-line tool that extracts frames from videos at specific timestamps, analyzes them using Anthropic's Claude AI vision capabilities, and stores the descriptions in MongoDB.

## Features

- Extract frames from videos at any timestamp
- AI-powered scene analysis using Claude Sonnet 4.5
- Structured JSON descriptions including:
  - Scene overview
  - Objects detected
  - Setting/location type
  - Time of day
  - Weather conditions
- MongoDB storage with automatic indexing
- Comprehensive error handling
- Support for verbose and JSON output modes

## Requirements

- Python 3.8 or higher
- MongoDB (running locally or remotely)
- Anthropic API key

## Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MongoDB:
   - Install MongoDB: https://www.mongodb.com/docs/manual/installation/
   - Start MongoDB service:
     ```bash
     # On Linux
     sudo systemctl start mongod

     # On macOS
     brew services start mongodb-community

     # On Windows
     net start MongoDB
     ```

4. Configure environment variables:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```
   - Get your API key from: https://console.anthropic.com/settings/keys

## Usage

### Basic Usage

Extract and analyze a frame at a specific timestamp (in seconds):

```bash
python -m src.main video.mp4 45.5
```

### Verbose Output

Show detailed processing information:

```bash
python -m src.main video.mp4 45.5 --verbose
```

### JSON Output

Get results in JSON format (useful for automation):

```bash
python -m src.main video.mp4 45.5 --output-json
```

### Examples

```bash
# Extract frame at 1 minute 30 seconds (90 seconds)
python -m src.main /path/to/my_video.mp4 90

# Analyze the first frame
python -m src.main video.mp4 0

# Get detailed output
python -m src.main video.mp4 45.5 --verbose
```

## Output

### Normal Mode

```
Processing video: /path/to/video.mp4
Extracting frame at timestamp: 45.5s
Analyzing frame with Claude API...
Storing results in MongoDB...
Success! Frame description stored with ID: 6583e1234567890abcdef123

Description: A person walking in a park during afternoon with sunny weather
Objects detected: person, trees, pathway, bench
Setting: outdoor park
Time of day: afternoon
Weather: sunny
```

### JSON Mode

```json
{
  "success": true,
  "document_id": "6583e1234567890abcdef123",
  "description": {
    "scene": "A person walking in a park during afternoon with sunny weather",
    "objects": ["person", "trees", "pathway", "bench"],
    "setting": "outdoor park",
    "time_of_day": "afternoon",
    "weather": "sunny"
  },
  "frame_metadata": {
    "video_filename": "video.mp4",
    "video_duration": 120.5,
    "video_fps": 30.0,
    "frame_number": 1365,
    "frame_dimensions": {
      "width": 1920,
      "height": 1080
    }
  },
  "api_metadata": {
    "model": "claude-sonnet-4.5-20250929",
    "tokens_used": 1250
  }
}
```

## MongoDB Schema

The tool stores frame descriptions in the following format:

**Database**: `video_analysis` (configurable)
**Collection**: `frame_descriptions` (configurable)

```json
{
  "_id": ObjectId("..."),
  "video_path": "/absolute/path/to/video.mp4",
  "timestamp": 45.5,
  "description": {
    "scene": "General scene description",
    "objects": ["list", "of", "objects"],
    "setting": "location type",
    "time_of_day": "afternoon",
    "weather": "sunny"
  },
  "frame_metadata": {
    "video_filename": "video.mp4",
    "video_duration": 120.5,
    "video_fps": 30.0,
    "frame_number": 1365,
    "frame_dimensions": {
      "width": 1920,
      "height": 1080
    }
  },
  "api_metadata": {
    "model": "claude-sonnet-4.5-20250929",
    "tokens_used": 1250
  },
  "created_at": ISODate("2025-12-28T...")
}
```

## Configuration

All configuration is done via environment variables in the `.env` file:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Your Anthropic API key |
| `MONGODB_URI` | No | `mongodb://localhost:27017/` | MongoDB connection string |
| `MONGODB_DATABASE` | No | `video_analysis` | Database name |
| `MONGODB_COLLECTION` | No | `frame_descriptions` | Collection name |
| `CLAUDE_MODEL` | No | `claude-sonnet-4.5-20250929` | Claude model to use |
| `MAX_TOKENS` | No | `1024` | Maximum tokens for API response |

## Supported Video Formats

The tool supports all video formats that OpenCV can read, including:
- MP4 (H.264, H.265)
- AVI
- MOV
- MKV
- WebM
- FLV

## Error Handling

The tool provides clear error messages and appropriate exit codes:

- **Exit Code 0**: Success
- **Exit Code 1**: Configuration or validation error
- **Exit Code 2**: Video processing error
- **Exit Code 3**: API error
- **Exit Code 4**: Database error

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
**Solution**: Create a `.env` file with your API key (see Installation step 4)

### "Cannot connect to MongoDB"
**Solutions**:
- Ensure MongoDB is running: `sudo systemctl status mongod`
- Start MongoDB: `sudo systemctl start mongod`
- Check the connection string in `.env`
- Test connection: `mongosh mongodb://localhost:27017/`

### "Video file not found"
**Solution**: Use an absolute path or verify the relative path is correct

### "Timestamp out of bounds"
**Solution**: The timestamp exceeds the video duration. The error message will show the video's actual duration.

### "Invalid video format"
**Solutions**:
- Ensure the video file is not corrupted
- Try converting to MP4: `ffmpeg -i input.avi output.mp4`
- Check that OpenCV supports your video codec

### "API rate limit exceeded"
**Solution**: Wait a moment and try again. Consider spacing out your requests.

## Querying Stored Data

You can query the stored descriptions using MongoDB:

```javascript
// Connect to MongoDB
mongosh

// Switch to database
use video_analysis

// Find all descriptions for a video
db.frame_descriptions.find({ video_path: "/path/to/video.mp4" })

// Find descriptions with specific objects
db.frame_descriptions.find({ "description.objects": "person" })

// Find recent descriptions
db.frame_descriptions.find().sort({ created_at: -1 }).limit(10)

// Count total descriptions
db.frame_descriptions.countDocuments()
```

## Project Structure

```
frame-description/
├── .env                       # Environment variables (git-ignored)
├── .env.example              # Template for configuration
├── .gitignore                # Git ignore patterns
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── src/
    ├── __init__.py           # Package initialization
    ├── main.py               # CLI entry point
    ├── video_processor.py    # Frame extraction with OpenCV
    ├── claude_client.py      # Anthropic API integration
    ├── database.py           # MongoDB operations
    ├── config.py             # Configuration loading
    └── exceptions.py         # Custom exception classes
```

## License

This project is provided as-is for demonstration purposes.

## Contributing

Feel free to submit issues or pull requests for improvements.
