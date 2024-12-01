import unittest
from unittest.mock import patch
from src.endpoints.smartthings_endpoint import SmartThingsEndpoint
import os

class TestSmartThingsEndpoint(unittest.TestCase):

    @patch("src.endpoints.smartthings_endpoint.requests.get")
    @patch.dict(os.environ, {"SMARTTHINGS_ACCESS_TOKEN": "mock-access-token"})
    def test_connect_successful(self, mock_get):
        mock_get.return_value.status_code = 200
        endpoint = SmartThingsEndpoint({
            'device_id': 'test-device-id'
        })
        self.assertTrue(endpoint.connect())

    @patch("src.endpoints.smartthings_endpoint.requests.get")
    def test_connect_no_token(self, mock_get):
        endpoint = SmartThingsEndpoint({
            'device_id': 'test-device-id'
        })
        self.assertFalse(endpoint.connect())

    @patch("src.endpoints.smartthings_endpoint.requests.post")
    @patch.dict(os.environ, {"SMARTTHINGS_ACCESS_TOKEN": "mock-access-token"})
    def test_set_color_successful(self, mock_post):
        mock_post.return_value.status_code = 200
        endpoint = SmartThingsEndpoint({
            'device_id': 'test-device-id'
        })
        self.assertTrue(endpoint.set_color((0.5, 0.5, 0.5)))

    @patch("src.endpoints.smartthings_endpoint.requests.post")
    def test_set_color_no_token(self, mock_post):
        endpoint = SmartThingsEndpoint({
            'device_id': 'test-device-id'
        })
        self.assertFalse(endpoint.set_color((0.5, 0.5, 0.5)))

if __name__ == "__main__":
    unittest.main()
