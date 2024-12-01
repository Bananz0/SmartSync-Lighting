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
        Initialize lighting endpoints based on configuration.

        Returns:
        list: Configured lighting endpoints.
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
            except Exception as e:
                print(f"Error initializing endpoint: {e}")

        return endpoints

    def _sync_lighting(self, track_info):
        """
        Synchronize lighting based on the current track.

        Args:
            track_info (dict): Current track information.
        """
        if not track_info or not track_info.get('album_art'):
            print("No track detected. Applying default color.")
            self._apply_default_color()
            return

        try:
            # Download album art and extract colors
            album_art = self.spotify_handler.download_album_art(track_info['album_art'])
            colors = ColorProcessor.extract_dominant_colors(album_art, num_colors=3, focus_center=True)

            # Select the best displayable color
            displayable_color = self._select_displayable_color(colors)

            # Debug the selected color
            print(f"Now playing: {track_info['name']} by {track_info['artist']}")
            print("Selected Displayable Color:")
            self._print_color(displayable_color)

            # Apply the selected color
            self._apply_color(displayable_color)

        except Exception as e:
            print(f"Lighting sync error: {e}")

    def _apply_default_color(self):
        """
        Apply a default color when no track is playing.
        """
        default_color = (255, 255, 255)  # Example: Warm white
        print("Applying default color:")
        self._print_color(default_color)
        self._apply_color(default_color)

    def _apply_color(self, color):
        """
        Apply the given color to all connected endpoints.

        Args:
            color (tuple): RGB color values (0-255 range).
        """
        if not color:
            print("No color to apply.")
            return

        for endpoint in self.endpoints:
            try:
                endpoint.set_color(color)
            except Exception as e:
                print(f"Error applying color to endpoint: {e}")

    def _print_color(self, rgb_color):
        """
        Print a visual representation of an RGB color in the terminal.

        Args:
            rgb_color (tuple): RGB color values (0-255 range).
        """
        r, g, b = rgb_color
        ansi_color = f"\033[48;2;{r};{g};{b}m   \033[0m"
        print(f"{ansi_color} RGB: {rgb_color}")

    def _select_displayable_color(self, colors):
        """
        Select the most displayable color from the extracted colors.

        Args:
        colors (dict): Extracted center and global colors.

        Returns:
        tuple: The selected RGB color.
        """
        center_colors = colors.get('center_colors', [])
        global_colors = colors.get('global_colors', [])
        all_colors = center_colors + global_colors

        for color in all_colors:
            normalized_color = ColorProcessor.normalize_color(color)
            if ColorProcessor.is_color_displayable(normalized_color):
                return color

        # Fallback: Return the first available color if none are displayable.
        return all_colors[0] if all_colors else (255, 255, 255)  # Default color fallback

    def _polling_loop(self):
        last_track_check = None
        retries = 0
        max_retries = 3

        while self.running:
            try:
                # Fetch the current track
                current_track = self.spotify_handler.get_current_track()

                # If the track has changed, update and sync lighting
                if current_track and current_track != self._current_track:
                    self._current_track = current_track
                    last_track_check = time.time()
                    retries = 0  # Reset retries on successful fetch
                    print(f"New track detected: {current_track['name']} by {current_track['artist']}")
                    self._sync_lighting(current_track)

                # If no track is returned, retry a few times
                elif not current_track and time.time() - (last_track_check or 0) > 10:  # Retry after 10 seconds
                    if retries < max_retries:
                        retries += 1
                        print(f"No track detected. Retrying track fetch... Attempt {retries}/{max_retries}")
                        continue
                    print("No track detected consistently. Setting default color.")
                    self._sync_lighting(None)
                    retries = 0  # Reset retries after applying default color

                time.sleep(self.config.config.get('spotify', {}).get('polling_interval', 5))

            except Exception as e:
                print(f"Polling loop error: {e}")
                time.sleep(5)

    def start(self):
        """
        Start the lighting synchronization.
        """
        if not self.test_mode and not self.endpoints:
            print("No endpoints configured. Cannot start.")
            return

        print("Starting SmartSync Lighting" + (" - TEST MODE" if self.test_mode else "") + "...")
        self.running = True
        self.poll_thread = threading.Thread(target=self._polling_loop)
        self.poll_thread.start()

    def stop(self):
        """
        Stop the lighting synchronization.
        """
        print("Stopping SmartSync Lighting...")
        self.running = False

        if not self.test_mode:
            for endpoint in self.endpoints:
                endpoint.disconnect()

        if hasattr(self, 'poll_thread'):
            self.poll_thread.join()
