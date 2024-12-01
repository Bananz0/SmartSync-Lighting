import os
import time

import requests
import json
from .base_endpoint import BaseEndpoint


class SmartThingsEndpoint(BaseEndpoint):
    def __init__(self, config):
        """
        Initialize the SmartThings endpoint.

        Args:
        config (dict): Configuration with `device_id`.
        """
        self.access_token = os.getenv('SMARTTHINGS_ACCESS_TOKEN')
        self.device_id = config.get('device_id')
        self.base_url = 'https://api.smartthings.com/v1'
        self.test_env = os.getenv('TEST_ENV', 'False').lower() == 'true'

        if not self.device_id:
            raise ValueError("Device ID is required for SmartThingsEndpoint.")

        if not self.access_token and not self.test_env:
            print("Warning: SMARTTHINGS_ACCESS_TOKEN is not set. This endpoint is currently inactive.")

    def connect(self):
        """
        Validate connection to SmartThings.

        Returns:
        bool: Connection status.
        """
        if not self.access_token:
            if not self.test_env:
                print("SmartThings token is not set. Skipping connection.")
            return False

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f'{self.base_url}/devices/{self.device_id}', headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"SmartThings connection error: {e}")
            return False

    def set_color(self, color, intensity=1.0):
        """
        Set device color and intensity.

        Args:
            color (tuple): RGB color values (0-1 range).
            intensity (float): Light intensity (0-1).
        """
        if not self.access_token:
            print("SmartThings token is not set. Skipping color update.")
            return False

        try:
            # Scale RGB to 0-255 range correctly
            rgb_color = tuple(int(c * 255) for c in color)

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'commands': [
                    {
                        'component': 'main',
                        'capability': 'switch',
                        'command': 'on'
                    },
                    {
                        'component': 'main',
                        'capability': 'colorControl',
                        'command': 'setColor',
                        'arguments': [{
                            'hue': self._rgb_to_hue(rgb_color),
                            'saturation': 100,  # Full saturation
                            'level': int(intensity * 100)
                        }]
                    }
                ]
            }

            print(f"Setting color to RGB: {rgb_color}, Hue: {self._rgb_to_hue(rgb_color)}")
            print(f"Payload Sent to SmartThings: {json.dumps(payload, indent=2)}")

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
        Disconnect from SmartThings (no-op for now).
        """
        print("SmartThingsEndpoint disconnect called. No action required.")
        return True

    def _rgb_to_hue(self, rgb):
        """
        Convert RGB to Hue value for SmartThings.

        Args:
            rgb (tuple): RGB color values (0-255 range).

        Returns:
            int: Hue value (0-360).
        """
        r, g, b = [x / 255.0 for x in rgb]
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn

        if mx == mn:
            return 0  # No hue for grayscale

        if mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        else:
            h = (60 * ((r - g) / df) + 240) % 360

        debug_hue = round(h)
        print(f"Converting RGB {rgb} to Hue: {debug_hue}")
        return debug_hue

    def test_color_mapping(self, test_colors):
        """
        Test SmartThings color mapping by sending controlled RGB values.

        Args:
            test_colors (list): List of RGB tuples (0-255 range) to test.
        """
        if not self.access_token:
            print("SmartThings token is not set. Cannot run color mapping test.")
            return

        for rgb_color in test_colors:
            try:
                hue = self._rgb_to_hue(rgb_color)
                payload = {
                    'commands': [
                        {
                            'component': 'main',
                            'capability': 'switch',
                            'command': 'on'
                        },
                        {
                            'component': 'main',
                            'capability': 'colorControl',
                            'command': 'setColor',
                            'arguments': [{
                                'hue': hue,
                                'saturation': 100,
                                'level': 100
                            }]
                        }
                    ]
                }

                print(f"Testing RGB: {rgb_color} -> Hue: {hue}")
                response = requests.post(
                    f'{self.base_url}/devices/{self.device_id}/commands',
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    },
                    json=payload
                )

                if response.status_code == 200:
                    print(f"RGB {rgb_color} successfully sent to device.")
                else:
                    print(f"Error sending RGB {rgb_color}: {response.status_code}, {response.text}")

                # Delay between tests to observe changes
                time.sleep(5)

            except Exception as e:
                print(f"Error during color mapping test for RGB {rgb_color}: {e}")


