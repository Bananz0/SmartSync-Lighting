import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SMARTTHINGS_ACCESS_TOKEN = os.getenv("SMARTTHINGS_ACCESS_TOKEN").strip()
SMARTTHINGS_DEVICE_ID = os.getenv("SMARTTHINGS_DEVICE_ID").strip()
POLLING_INTERVAL = 10  # Set polling interval in seconds

def fetch_device_state():
    """
    Fetch the device state from SmartThings API.
    """
    url = f"https://api.smartthings.com/v1/devices/{SMARTTHINGS_DEVICE_ID}/status"
    headers = {
        "Authorization": f"Bearer {SMARTTHINGS_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error querying device state: {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

def watch_device_state():
    """
    Continuously watch the device state until interrupted.
    """
    print("Starting to monitor device state. Press Ctrl+C to stop.")
    try:
        while True:
            state = fetch_device_state()
            if state:
                print("Device State:")
                print(state)
            else:
                print("Failed to fetch device state.")

            # Wait before polling again
            time.sleep(POLLING_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopped monitoring device state.")

if __name__ == "__main__":
    if not SMARTTHINGS_ACCESS_TOKEN or not SMARTTHINGS_DEVICE_ID:
        print("SMARTTHINGS_ACCESS_TOKEN and SMARTTHINGS_DEVICE_ID must be set in the .env file.")
    else:
        watch_device_state()
