import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from io import BytesIO


class SpotifyHandler:
    def __init__(self, config_loader):
        credentials = config_loader.get_spotify_credentials()
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            redirect_uri=credentials['redirect_uri'],
            scope="user-read-currently-playing"
        ))

    def get_current_track(self):
        """
        Retrieve currently playing track information

        Returns:
        dict: Track information including name, artist, album art URL
        """
        try:
            current_track = self.sp.current_user_playing_track()
            if current_track and current_track['is_playing']:
                track = current_track['item']
                return {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None
                }
            return None
        except Exception as e:
            print(f"Error fetching current track: {e}")
            return None

    def download_album_art(self, art_url):
        """
        Download album art from URL

        Args:
        art_url (str): URL of the album art

        Returns:
        bytes: Image data
        """
        if not art_url:
            return None

        try:
            response = requests.get(art_url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading album art: {e}")
            return None