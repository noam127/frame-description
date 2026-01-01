import base64
import json
import anthropic
from .exceptions import (
    AnthropicAPIError,
    APIConnectionError,
    APITimeoutError,
    APIRateLimitError,
    APIBadResponseError,
    JSONParseError
)


ANALYSIS_PROMPT = """Analyze this video frame and provide a detailed scene description.

Include:
1. A general description of what's happening
2. Key objects, people, or elements visible
3. The type of setting or location
4. Time of day (if determinable)
5. Weather conditions (if visible)

Return as valid JSON:
{
  "scene": "brief overall description",
  "objects": ["list", "of", "key", "objects"],
  "setting": "location type",
  "time_of_day": "morning/afternoon/evening/night/unclear",
  "weather": "sunny/cloudy/rainy/snowy/indoor/unclear"
}"""


def describe_frame(frame_jpeg_bytes: bytes, api_key: str, model: str, max_tokens: int) -> dict:
    """Get a description of a video frame using Claude's vision API.

    Returns in a dictionary:
        - description: Parsed JSON description from Claude
        - tokens_used: Number of tokens used
        - model: Model that was used
    """
    try:
        # Encode frame to base64
        base64_image = base64.standard_b64encode(frame_jpeg_bytes).decode("utf-8")

        # Create Anthropic client
        client = anthropic.Anthropic(api_key=api_key)

        # Make API request
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": ANALYSIS_PROMPT
                        }
                    ]
                }
            ]
        )

        # Extract text content from response
        if not response.content or len(response.content) == 0:
            raise APIBadResponseError("Empty response from Claude API")

        text_content = None
        for block in response.content:
            if hasattr(block, 'text'):
                text_content = block.text
                break

        if text_content is None:
            raise APIBadResponseError("No text content in Claude API response")

        # Try to find JSON in the response (Claude might include extra text)
        # Look for JSON object boundaries
        start_idx = text_content.find('{')
        end_idx = text_content.rfind('}')

        if start_idx == -1 or end_idx == -1:
            raise JSONParseError(
                f"No JSON object found in response: {text_content[:200]}"
            )

        json_str = text_content[start_idx:end_idx + 1]
        
        # Parse JSON from response
        try:
            description = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise JSONParseError(
                f"Failed to parse JSON from Claude response: {str(e)}\n"
                f"Response text: {text_content[:200]}"
            )

        # Validate JSON structure
        required_fields = ["scene", "objects", "setting", "time_of_day", "weather"]
        missing_fields = [field for field in required_fields if field not in description]

        if missing_fields:
            raise JSONParseError(
                f"Response JSON missing required fields: {missing_fields}\n"
                f"Got: {description}"
            )

        # Get token usage
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        return {
            "description": description,
            "tokens_used": tokens_used,
            "model": model
        }

    except anthropic.RateLimitError as e:
        raise APIRateLimitError(
            f"API rate limit exceeded: {str(e)}. Please wait and try again."
        )
    except anthropic.APITimeoutError as e:
        raise APITimeoutError(
            f"API request timed out: {str(e)}. Check your internet connection."
        )
    except anthropic.APIConnectionError as e:
        raise APIConnectionError(
            f"Failed to connect to Anthropic API: {str(e)}. "
            "Check your internet connection and API key."
        )
    except anthropic.APIError as e:
        raise AnthropicAPIError(str(e))
