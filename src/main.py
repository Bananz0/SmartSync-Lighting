import sys
import signal
from src.utils.config_loader import ConfigLoader  # Change this import
from src.core.lighting_orchestrator import LightingOrchestrator  # And this one


def signal_handler(sig, frame):
    """
    Handle keyboard interrupt (Ctrl+C)
    """
    print("\nInterrupted. Stopping SmartSync Lighting...")
    if orchestrator:
        orchestrator.stop()
    sys.exit(0)


def main():
    global orchestrator

    try:
        # Load configuration
        config_loader = ConfigLoader()

        # Create lighting orchestrator
        orchestrator = LightingOrchestrator(config_loader)

        # Register signal handler
        signal.signal(signal.SIGINT, signal_handler)

        # Start lighting synchronization
        orchestrator.start()

        # Keep main thread running
        signal.pause()

    except Exception as e:
        print(f"Error starting SmartSync Lighting: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()