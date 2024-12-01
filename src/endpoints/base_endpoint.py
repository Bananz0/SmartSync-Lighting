from abc import ABC, abstractmethod


class BaseEndpoint(ABC):
    """
    Abstract base class for smart lighting endpoints
    """

    @abstractmethod
    def connect(self):
        """Establish connection to the platform"""
        pass

    @abstractmethod
    def set_color(self, color, intensity=1.0):
        """Set the color and intensity of the lights"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the connection to the platform"""
        pass