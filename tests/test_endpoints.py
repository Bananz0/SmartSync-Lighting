import unittest
from unittest.mock import patch
from src.endpoints.smartthings_endpoint import SmartThingsEndpoint
from dotenv import load_dotenv


class TestSmartThingsEndpoint(unittest.TestCase):

    @patch("src.endpoints.smartthings_endpoint.os.getenv", side_effect=lambda key, default=None: "mock-access-token" if key == "SMARTTHINGS_ACCESS_TOKEN" else default)
    @patch("src.endpoints.smartthings_endpoint.requests.get")
    def test_connect_successful(self, mock_get, mock_getenv):
        """
        Test that the connect method works when the access token is provided.
        """
        load_dotenv()  # Ensure .env is loaded if needed
        mock_get.return_value.status_code = 200
        endpoint = SmartThingsEndpoint({
            'device_id': 'test-device-id'
        })
        self.assertTrue(endpoint.connect())

    @patch("src.endpoints.smartthings_endpoint.os.getenv", side_effect=lambda key, default=None: None if key == "SMARTTHINGS_ACCESS_TOKEN" else default)
    @patch("src.endpoints.smartthings_endpoint.requests.get")
    def test_connect_no_token(self, mock_get, mock_getenv):
        """
        Test that the connect method fails when the access token is not provided.
        """
        mock_get.return_value.status_code = 401  # Simulate unauthorized response
        endpoint = SmartThingsEndpoint({
            'device_id': 'test-device-id'
        })
        self.assertFalse(endpoint.connect())

    @patch("src.endpoints.smartthings_endpoint.os.getenv", side_effect=lambda key, default=None: "mock-access-token" if key == "SMARTTHINGS_ACCESS_TOKEN" else default)
    @patch("src.endpoints.smartthings_endpoint.requests.post")
    def test_set_color_successful(self, mock_post, mock_getenv):
        """
        Test that the set_color method works when the access token is provided.
        """
        mock_post.return_value.status_code = 200
        endpoint = SmartThingsEndpoint({
            'device_id': 'test-device-id'
        })
        self.assertTrue(endpoint.set_color((0.5, 0.5, 0.5)))

    @patch("src.endpoints.smartthings_endpoint.os.getenv", side_effect=lambda key, default=None: None if key == "SMARTTHINGS_ACCESS_TOKEN" else default)
    @patch("src.endpoints.smartthings_endpoint.requests.post")
    def test_set_color_no_token(self, mock_post, mock_getenv):
        """
        Test that the set_color method fails when the access token is not provided.
        """
        mock_post.return_value.status_code = 401  # Simulate unauthorized response
        endpoint = SmartThingsEndpoint({
            'device_id': 'test-device-id'
        })
        self.assertFalse(endpoint.set_color((0.5, 0.5, 0.5)))


if __name__ == "__main__":
    unittest.main()
