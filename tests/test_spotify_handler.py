import unittest
from unittest.mock import patch, MagicMock
from src.core.spotify_handler import SpotifyHandler

class TestSpotifyHandler(unittest.TestCase):

    @patch("src.core.spotify_handler.SpotifyOAuth")
    @patch("src.core.spotify_handler.spotipy.Spotify")
    def test_get_current_track_success(self, mock_spotify, mock_oauth):
        mock_instance = mock_spotify.return_value
        mock_instance.current_user_playing_track.return_value = {
            'is_playing': True,
            'item': {
                'name': 'Test Song',
                'artists': [{'name': 'Test Artist'}],
                'album': {'images': [{'url': 'https://test-image.url'}]}
            }
        }
        spotify_handler = SpotifyHandler(MagicMock())
        track = spotify_handler.get_current_track()
        self.assertEqual(track['name'], 'Test Song')
        self.assertEqual(track['artist'], 'Test Artist')

    @patch("src.core.spotify_handler.SpotifyOAuth")
    @patch("src.core.spotify_handler.spotipy.Spotify")
    def test_get_current_track_no_song(self, mock_spotify, mock_oauth):
        mock_instance = mock_spotify.return_value
        mock_instance.current_user_playing_track.return_value = None
        spotify_handler = SpotifyHandler(MagicMock())
        self.assertIsNone(spotify_handler.get_current_track())

    @patch("src.core.spotify_handler.requests.get")
    def test_download_album_art_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'test-image-data'
        spotify_handler = SpotifyHandler(MagicMock())
        album_art = spotify_handler.download_album_art('https://test-image.url')
        self.assertEqual(album_art, b'test-image-data')

    @patch("src.core.spotify_handler.requests.get")
    def test_download_album_art_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.return_value.content = None  # Explicitly set content to None
        spotify_handler = SpotifyHandler(MagicMock())
        album_art = spotify_handler.download_album_art('https://test-image.url')
        self.assertIsNone(album_art)

