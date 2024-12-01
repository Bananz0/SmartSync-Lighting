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

    def set_color(self, rgb):
        """
        Set device color based on RGB values.

        Args:
            rgb (tuple): RGB color values (0-255 range).
        """
        if not self.access_token:
            print("SmartThings token is not set. Skipping color update.")
            return False

        try:
            hue_data = self._rgb_to_hue(rgb)
            hue_degrees = hue_data["hue"]
            saturation = hue_data["saturation"]
            level = hue_data["level"]

            # **Convert hue degrees to hue percentage (0-100)**
            hue = (hue_degrees / 360) * 100

            payload = {
                "commands": [
                    {"component": "main", "capability": "switch", "command": "on"},
                    {
                        "component": "main",
                        "capability": "colorControl",
                        "command": "setColor",
                        "arguments": [{"hue": hue, "saturation": saturation, "level": level}],
                    },
                ]
            }

            print(f"Setting color to RGB: {rgb}, Hue: {hue}%, Saturation: {saturation}%, Level: {level}%")
            response = requests.post(
                f"{self.base_url}/devices/{self.device_id}/commands",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            print(f"Response: {response.status_code}, {response.json()}")
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

    @staticmethod
    def _rgb_to_hue(rgb):
        """
        Convert RGB to Hue, Saturation, and Level values.

        Args:
            rgb (tuple): RGB color values (0-255 range).

        Returns:
            dict: Hue (0-360), Saturation (0-100), Level (0-100).
        """
        r, g, b = [x / 255.0 for x in rgb]
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        chroma = cmax - cmin

        # Level (Brightness)
        level = cmax * 100

        # Saturation
        saturation = 0 if cmax == 0 else (chroma / cmax) * 100

        # Hue
        if chroma == 0:
            hue = 0
        elif cmax == r:
            hue = (60 * ((g - b) / chroma) + 360) % 360
        elif cmax == g:
            hue = (60 * ((b - r) / chroma) + 120) % 360
        else:
            hue = (60 * ((r - g) / chroma) + 240) % 360

        print(f"Converted RGB {rgb} -> Hue: {round(hue)}, Saturation: {round(saturation)}, Level: {round(level)}")
        return {
            "hue": round(hue),
            "saturation": round(saturation),
            "level": round(level),
        }

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
                print(f"Response: {response.status_code}, {response.json()}")

                if response.status_code == 200:
                    print(f"RGB {rgb_color} successfully sent to device.")
                else:
                    print(f"Error sending RGB {rgb_color}: {response.status_code}, {response.text}")

                # Delay between tests to observe changes
                time.sleep(5)

            except Exception as e:
                print(f"Error during color mapping test for RGB {rgb_color}: {e}")

    def set_color_from_payload(self, payload):
        """
        Send a pre-crafted payload to the SmartThings device.

        Args:
            payload (dict): Pre-crafted payload to send.
        """
        if not self.access_token:
            print("SmartThings token is not set. Skipping color update.")
            return False

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            print(f"Sending payload to SmartThings: {payload}")
            response = requests.post(
                f'{self.base_url}/devices/{self.device_id}/commands',
                headers=headers,
                json=payload
            )
            print(f"Response: {response.status_code}, {response.json()}")
            return response.status_code == 200

        except Exception as e:
            print(f"SmartThings payload sending error: {e}")
            return False

    def get_device_capabilities(self):
        """
        Fetch capabilities of the device from SmartThings API.

        Returns:
        list: List of supported capabilities.
        """
        if not self.access_token:
            raise ValueError("SmartThings token is not set.")

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            url = f'{self.base_url}/devices/{self.device_id}/components/main/capabilities'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return [cap['id'] for cap in response.json()['items']]
        except Exception as e:
            print(f"Error fetching capabilities: {e}")
            return []

    def get_device_state(self):
        """
        Query the SmartThings API for the current device state.

        Returns:
        dict: The current state of the device.
        """
        if not self.access_token:
            raise ValueError("SmartThings access token is missing.")

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }

        url = f"{self.base_url}/devices/{self.device_id}/components/main/status"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Error querying device state: {e}")