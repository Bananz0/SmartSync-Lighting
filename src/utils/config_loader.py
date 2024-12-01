import os
import yaml
import json
from dotenv import load_dotenv


class ConfigLoader:
    def __init__(self, config_path=None, endpoints_path=None):
        """
        Initialize ConfigLoader and load configurations.

        Args:
            config_path (str): Path to the YAML configuration file.
            endpoints_path (str): Path to the JSON endpoints file.
        """
        # Load environment variables
        load_dotenv()

        # Default file paths (can be overridden via arguments or environment variables)
        self.config_path = config_path or os.getenv('CONFIG_PATH', 'config/config.yaml')
        self.endpoints_path = endpoints_path or os.getenv('ENDPOINTS_PATH', 'config/endpoints.json')

        # Load YAML configuration
        self.config = self._load_yaml(self.config_path)

        # Load endpoints configuration
        self.endpoints = self._load_json(self.endpoints_path)

    def _load_yaml(self, path):
        """
        Load a YAML file safely.

        Args:
            path (str): Path to the YAML file.

        Returns:
            dict: Parsed YAML content.
        """
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: YAML configuration file not found at {path}. Using defaults.")
            return {}
        except yaml.YAMLError as e:
            print(f"Error: Failed to parse YAML configuration file at {path}. {e}")
            return {}

    def _load_json(self, path):
        """
        Load a JSON file safely.

        Args:
            path (str): Path to the JSON file.

        Returns:
            list: Parsed JSON content.
        """
        try:
            with open(path, 'r') as f:
                return json.load(f) or []
        except FileNotFoundError:
            print(f"Warning: JSON endpoints file not found at {path}. Using defaults.")
            return []
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON endpoints file at {path}. {e}")
            return []

    def get_spotify_credentials(self):
        """
        Retrieve Spotify API credentials from environment variables.

        Returns:
            dict: Spotify credentials.
        """
        credentials = {
            'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
            'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
            'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
        }

        # Check for missing credentials
        missing = [key for key, value in credentials.items() if not value]
        if missing:
            print(f"Warning: Missing Spotify credentials: {', '.join(missing)}")

        return credentials

    def get_endpoints(self):
        """
        Return the list of configured endpoints.

        Returns:
            list: Endpoints configuration.
        """
        if not self.endpoints:
            print("Warning: No endpoints configured in endpoints.json.")
        return self.endpoints
