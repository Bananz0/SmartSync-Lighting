import time
import threading
from src.utils.config_loader import ConfigLoader
from src.core.lighting_orchestrator import LightingOrchestrator


def main():
    # Load configuration
    config_loader = ConfigLoader()

    # Create lighting orchestrator in test mode
    orchestrator = LightingOrchestrator(config_loader, test_mode=True)

    try:
        # Start lighting synchronization
        orchestrator.start()

        # Keep main thread running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        orchestrator.stop()


if __name__ == "__main__":
    main()