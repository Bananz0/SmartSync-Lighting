import os
import time
import json
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from src.endpoints.smartthings_endpoint import SmartThingsEndpoint

# Load environment variables
load_dotenv()

def plot_color_graph(results):
    """
    Plot a graph to visualize hue and saturation mapping.

    Args:
        results (list): List of dictionaries containing hue, saturation, and observed colors.
    """
    hues = [result['input']['hue'] for result in results]
    saturations = [result['input']['saturation'] for result in results]
    observed_colors = [result['observed_color'] for result in results]

    # Map saturation and hue into 2D visualization
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(hues, saturations, c=hues, cmap='hsv', s=100, edgecolors='black')

    # Annotate points with observed colors
    for i, color in enumerate(observed_colors):
        plt.text(hues[i], saturations[i] + 2, color, fontsize=8, ha='center')

    plt.title("Hue and Saturation Mapping")
    plt.xlabel("Hue (0-360)")
    plt.ylabel("Saturation (0-100)")
    plt.colorbar(scatter, label="Hue")
    plt.grid(True)
    plt.show()

def test_colors(endpoint, test_data):
    """
    Test hue and saturation values on the device and record results.

    Args:
        endpoint (SmartThingsEndpoint): The SmartThings API endpoint.
        test_data (list): List of dictionaries with hue, saturation, and expected results.

    Returns:
        list: Results of the test with observed and expected values.
    """
    results = []

    for iteration, test in enumerate(test_data, 1):
        print(f"\nIteration {iteration}: Testing Hue: {test['hue']}, Saturation: {test['saturation']}")

        # Prepare payload
        payload = {
            'commands': [
                {
                    'component': 'main',
                    'capability': 'colorControl',
                    'command': 'setColor',
                    'arguments': [{
                        'hue': test['hue'],
                        'saturation': test['saturation'],
                        'level': test['level']
                    }]
                }
            ]
        }

        # Send the color command to the device
        success = endpoint.set_color_from_payload(payload)
        if success:
            print("Color set successfully. Fetching device state...")
            try:
                state = endpoint.get_device_state()
                print(f"Device State: {json.dumps(state, indent=2)}")

                # Record observed state
                results.append({
                    "iteration": iteration,
                    "input": {
                        "hue": test['hue'],
                        "saturation": test['saturation'],
                        "level": test['level']
                    },
                    "observed_color": state.get('components', {}).get('main', {}).get('colorControl', {}).get('color', {}).get('value', "Unknown")
                })
            except Exception as e:
                print(f"Error fetching device state: {e}")
                results.append({
                    "iteration": iteration,
                    "input": {
                        "hue": test['hue'],
                        "saturation": test['saturation'],
                        "level": test['level']
                    },
                    "observed_color": "Error fetching state"
                })
        else:
            print("Failed to set color.")
            results.append({
                "iteration": iteration,
                "input": {
                    "hue": test['hue'],
                    "saturation": test['saturation'],
                    "level": test['level']
                },
                "observed_color": "Failed to set color"
            })

        time.sleep(5)  # Delay for observation

    return results

if __name__ == "__main__":
    # Load device ID from .env
    device_id = os.getenv('SMARTTHINGS_DEVICE_ID')
    if not device_id:
        print("SMARTTHINGS_DEVICE_ID not found in environment variables.")
        exit(1)

    # Initialize the SmartThings endpoint
    endpoint = SmartThingsEndpoint({'device_id': device_id})

    # Define test hues and saturations
    test_data = [
        {"hue": 0, "saturation": 100, "level": 50, "expected": "Red"},
        {"hue": 32, "saturation": 100, "level": 50, "expected": "Green"},
        {"hue": 67, "saturation": 100, "level": 50, "expected": "Blue"},
        {"hue": 50, "saturation": 100, "level": 50, "expected": "Cyan"},
        {"hue": 12, "saturation": 0, "level": 50, "expected": "White"}
    ]

    # Perform the tests
    print("Starting color tests...")
    results = test_colors(endpoint, test_data)

    # Display results
    print("\nTest Results:")
    for result in results:
        print(result)

    # Plot results
    plot_color_graph(results)
