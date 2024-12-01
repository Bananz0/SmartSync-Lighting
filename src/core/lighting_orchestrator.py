import time
import threading
from ..utils.config_loader import ConfigLoader
from .spotify_handler import SpotifyHandler
from .color_processor import ColorProcessor


class LightingOrchestrator:
    def __init__(self, config_loader, test_mode=False):
        self.config = config_loader
        self.test_mode = test_mode
        self.spotify_handler = SpotifyHandler(config_loader)
        self.endpoints = self._initialize_endpoints() if not test_mode else []
        self.running = False
        self._current_track = None

    def _initialize_endpoints(self):
        """
        Initialize lighting endpoints based on configuration

        Returns:
        list: Configured lighting endpoints
        """
        if self.test_mode:
            return []

        endpoints = []
        endpoint_configs = self.config.get_endpoints()

        for endpoint_config in endpoint_configs:
            try:
                if endpoint_config['type'] == 'smartthings':
                    from ..endpoints.smartthings_endpoint import SmartThingsEndpoint
                    endpoint = SmartThingsEndpoint(endpoint_config)
                    if endpoint.connect():
                        endpoints.append(endpoint)
                    else:
                        print(f"Failed to connect to SmartThings endpoint: {endpoint_config}")
                # Add more endpoint types here in future
            except Exception as e:
                print(f"Error initializing endpoint: {e}")

        return endpoints

    def _sync_lighting(self, track_info):
        """
        Synchronize lighting based on current track

        Args:
        track_info (dict): Current track information
        """
        if not track_info or not track_info.get('album_art'):
            return

        try:
            # Download album art
            album_art = self.spotify_handler.download_album_art(track_info['album_art'])

            if album_art:
                # Extract dominant color
                color = ColorProcessor.extract_dominant_color(album_art)

                # Normalize color
                normalized_color = ColorProcessor.normalize_color(color)

                # In test mode, just print the color
                if self.test_mode:
                    print(f"Test Mode - Track: {track_info['name']} by {track_info['artist']}")
                    print(f"Extracted Color (RGB): {color}")
                    print(f"Normalized Color: {normalized_color}\n")
                else:
                    # Set color on all endpoints
                    for endpoint in self.endpoints:
                        try:
                            endpoint.set_color(normalized_color)
                        except Exception as e:
                            print(f"Error syncing endpoint: {e}")

        except Exception as e:
            print(f"Lighting sync error: {e}")

    def _polling_loop(self):
        """
        Continuous polling loop to check current track and sync lighting
        """
        while self.running:
            try:
                # Get current track
                current_track = self.spotify_handler.get_current_track()

                # Check if track has changed
                if current_track and current_track != self._current_track:
                    self._current_track = current_track
                    print(f"Now playing: {current_track['name']} by {current_track['artist']}")

                    # Sync lighting
                    self._sync_lighting(current_track)

                # Polling interval from config
                time.sleep(self.config.config['spotify']['polling_interval'])

            except Exception as e:
                print(f"Polling loop error: {e}")
                time.sleep(5)  # Wait before retrying

    def start(self):
        """
        Start the lighting synchronization
        """
        if not self.test_mode and not self.endpoints:
            print("No endpoints configured. Cannot start.")
            return

        print("Starting SmartSync Lighting" + (" - TEST MODE" if self.test_mode else "") + "...")
        self.running = True

        # Start polling in a separate thread
        self.poll_thread = threading.Thread(target=self._polling_loop)
        self.poll_thread.start()

    def stop(self):
        """
        Stop the lighting synchronization
        """
        print("Stopping SmartSync Lighting...")
        self.running = False

        # Close all endpoints
        if not self.test_mode:
            for endpoint in self.endpoints:
                endpoint.disconnect()

        # Wait for polling thread to finish
        if hasattr(self, 'poll_thread'):
            self.poll_thread.join()