import os
import yaml
import json
from dotenv import load_dotenv


class ConfigLoader:
    def __init__(self, config_path='config/config.yaml', endpoints_path='config/endpoints.json'):
        # Load environment variables
        load_dotenv()

        # Load YAML configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Load endpoints configuration
        with open(endpoints_path, 'r') as f:
            self.endpoints = json.load(f)

    def get_spotify_credentials(self):
        """Retrieve Spotify API credentials"""
        return {
            'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
            'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
            'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
        }

    def get_endpoints(self):
        """Return configured endpoints"""
        return self.endpoints