import time
import threading
import argparse
from src.utils.config_loader import ConfigLoader
from src.core.lighting_orchestrator import LightingOrchestrator

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the SmartSync Lighting application.")
    parser.add_argument("--test-mode", action="store_true", help="Run the application in test mode.")
    args = parser.parse_args()

    # Load configuration
    config_loader = ConfigLoader()

    # Initialize Lighting Orchestrator
    orchestrator = LightingOrchestrator(config_loader, test_mode=args.test_mode)

    try:
        # Start lighting synchronization
        orchestrator.start()

        # Keep main thread running
        while orchestrator.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        orchestrator.stop()

if __name__ == "__main__":
    main()
