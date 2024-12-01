import numpy as np
from PIL import Image
import io


class ColorProcessor:
    @staticmethod
    def extract_dominant_colors(image_data, num_colors=3):
        """
        Extract multiple dominant colors using k-means clustering.

        Args:
        image_data (bytes): Raw image data
        num_colors (int): Number of dominant colors to extract

        Returns:
        list: List of RGB color tuples, sorted by dominance
        """
        try:
            return ColorProcessor._extract_colors_opencv(image_data, num_colors)
        except ImportError:
            return ColorProcessor._extract_colors_pil(image_data, num_colors)
        except Exception as e:
            print(f"Color extraction error: {e}")
            return [(255, 255, 255)] * num_colors  # Default to white

    @staticmethod
    def _extract_colors_opencv(image_data, num_colors):
        """
        Extract dominant colors using OpenCV (k-means clustering).

        Args:
        image_data (bytes): Raw image data
        num_colors (int): Number of dominant colors to extract

        Returns:
        list: List of RGB color tuples
        """
        import cv2

        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((100, 100))  # Resize for faster processing
        np_image = np.array(image)
        pixels = np_image.reshape((-1, 3))
        pixels = np.float32(pixels)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        flags = cv2.KMEANS_RANDOM_CENTERS

        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, flags)

        # Count points in each cluster
        _, counts = np.unique(labels, return_counts=True)

        # Sort clusters by size
        sorted_indices = np.argsort(-counts)
        sorted_colors = [tuple(map(int, centers[i])) for i in sorted_indices]

        return sorted_colors[:num_colors]

    @staticmethod
    def _extract_colors_pil(image_data, num_colors):
        """
        Extract dominant colors using PIL (average color method).

        Args:
        image_data (bytes): Raw image data
        num_colors (int): Number of dominant colors to extract

        Returns:
        list: List of RGB color tuples
        """
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((100, 100)).convert("RGB")
        np_image = np.array(image).reshape((-1, 3))

        # Use numpy to find unique colors and sort them by frequency
        unique, counts = np.unique(np_image, axis=0, return_counts=True)
        sorted_indices = np.argsort(-counts)
        sorted_colors = [tuple(unique[i]) for i in sorted_indices]

        return sorted_colors[:num_colors]

    @staticmethod
    def normalize_color(color, max_intensity=255):
        """
        Normalize color to a 0-1 range.

        Args:
        color (tuple): RGB color values
        max_intensity (int): Maximum color intensity

        Returns:
        tuple: Normalized RGB color values
        """
        return tuple(c / max_intensity for c in color)

    @staticmethod
    def preview_colors(colors):
        """
        Print a preview of colors in the terminal using ANSI escape sequences.

        Args:
        colors (list): List of RGB color tuples
        """
        print("Color Previews:")
        for color in colors:
            r, g, b = color
            ansi_color = f"\033[48;2;{r};{g};{b}m   \033[0m"
            print(f"{ansi_color} RGB: {color}")
