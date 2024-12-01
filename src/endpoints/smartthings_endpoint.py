import requests
from .base_endpoint import BaseEndpoint
import os


class SmartThingsEndpoint(BaseEndpoint):
    def __init__(self, config):
        self.access_token = os.getenv('SMARTTHINGS_ACCESS_TOKEN')
        self.device_id = config.get('device_id')
        self.base_url = 'https://api.smartthings.com/v1'

        if not self.access_token or not self.device_id:
            raise ValueError("SmartThings configuration incomplete")

    def connect(self):
        """
        Validate connection to SmartThings

        Returns:
        bool: Connection status
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f'{self.base_url}/devices/{self.device_id}',
                headers=headers
            )

            return response.status_code == 200
        except Exception as e:
            print(f"SmartThings connection error: {e}")
            return False

    def set_color(self, color, intensity=1.0):
        """
        Set device color and intensity

        Args:
        color (tuple): RGB color values (0-1 range)
        intensity (float): Light intensity (0-1)
        """
        try:
            # Convert normalized color to 0-255 range
            rgb_color = tuple(int(c * 255) for c in color)

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'commands': [{
                    'component': 'main',
                    'capability': 'colorControl',
                    'command': 'setColor',
                    'arguments': [{
                        'hue': self._rgb_to_hue(rgb_color),
                        'saturation': 100,  # Full saturation
                        'level': int(intensity * 100)
                    }]
                }]
            }

            response = requests.post(
                f'{self.base_url}/devices/{self.device_id}/commands',
                headers=headers,
                json=payload
            )

            return response.status_code == 200
        except Exception as e:
            print(f"SmartThings color setting error: {e}")
            return False

    def disconnect(self):
        """
        Close connection (no-op for SmartThings)
        """
        return True

    def _rgb_to_hue(self, rgb):
        """
        Convert RGB to Hue value for SmartThings

        Args:
        rgb (tuple): RGB color values (0-255 range)

        Returns:
        int: Hue value (0-360)
        """
        r, g, b = [x / 255.0 for x in rgb]
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn

        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360

        return int(h)