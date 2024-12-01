import time
import threading

from ..endpoints.smartthings_endpoint import SmartThingsEndpoint
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
        self._last_applied_color = None  #

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
            # Use focus_percentage instead of focus_center
            colors = ColorProcessor.extract_dominant_colors(album_art, num_colors=3, focus_percentage=50)

            # Select the best displayable color
            displayable_color = self._select_displayable_color(colors)
            converted_color = SmartThingsEndpoint._rgb_to_hue(displayable_color)

            print(f"Now playing: {track_info['name']} by {track_info['artist']}")
            print(f"Selected RGB: {displayable_color}, Converted to HSL: {converted_color}")

            # Apply the selected color
            self._apply_color(displayable_color)

        except Exception as e:
            print(f"Lighting sync error: {e}")

    def _apply_default_color(self):
        """
        Apply a default color when no track is playing..
        """
        default_color = (255, 255, 255)  # Example: Warm white
        print("Applying default color:")
        self._print_color(default_color)
        self._apply_color(default_color)

    def _apply_color(self, color):
        """
        Apply the given color to all connected endpoints only if it has changed.

        Args:
            color (tuple): RGB color values (0-255 range).
        """
        if not color:
            print("No color to apply.")
            return

        if hasattr(self, "_last_applied_color") and color == self._last_applied_color:
            # Suppress logs for unchanged colors
            print(f"Color unchanged: {color}. Skipping update.")
            return

        self._last_applied_color = color  # Update the last applied color

        # **Add this line to print the color preview**
        self._print_color(color)

        for endpoint in self.endpoints:
            try:
                # Call set_color with the RGB tuple
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

        # Remove duplicate colors
        all_colors = [tuple(color) for color in {tuple(c) for c in all_colors}]

        # **Filter out dark colors**
        filtered_colors = [color for color in all_colors if not ColorProcessor.is_color_too_dark(color)]

        # **Attempt to select a displayable color**
        for color in filtered_colors:
            if ColorProcessor.is_color_displayable(color):
                return color

        # Fallback: Return a default color if none are suitable
        return (255, 255, 255)  # Default to white

    def _polling_loop(self):
        last_track_check = None
        retries = 0
        max_retries = 3
        no_track_logged = False  # Flag to avoid repeated "No track detected" logs

        while self.running:
            try:
                current_track = self.spotify_handler.get_current_track()

                if current_track and current_track != self._current_track:
                    self._current_track = current_track
                    last_track_check = time.time()
                    retries = 0
                    no_track_logged = False  # Reset the flag
                    print(f"New track detected: {current_track['name']} by {current_track['artist']}")
                    self._sync_lighting(current_track)

                elif not current_track and time.time() - (last_track_check or 0) > 10:
                    if retries < max_retries:
                        retries += 1
                        if not no_track_logged:  # Log once
                            print(f"No track detected. Retrying track fetch... Attempt {retries}/{max_retries}")
                            no_track_logged = True
                        continue

                    if not no_track_logged:  # Log only if not already logged
                        print("No track detected consistently. Setting default color.")
                        no_track_logged = True

                    self._sync_lighting(None)
                    retries = 0

                time.sleep(self.config.config.get("spotify", {}).get("polling_interval", 5))

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
