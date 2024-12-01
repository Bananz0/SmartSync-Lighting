from dotenv import load_dotenv
import os
from src.endpoints.smartthings_endpoint import SmartThingsEndpoint

# Load environment variables from .env
load_dotenv()

if __name__ == "__main__":
    # Test SmartThings color mapping
    test_colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 255),  # Cyan
        (255, 0, 255),  # Magenta
        (255, 255, 255),# White
        (128, 128, 128) # Gray
    ]

    # Replace 'your-device-id' with the actual device ID
    endpoint = SmartThingsEndpoint({'device_id': 'f13c8e3d-0965-49e7-80aa-ae0f5cdea316'})
    endpoint.test_color_mapping(test_colors)

