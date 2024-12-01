import numpy as np
from PIL import Image
import io


class ColorProcessor:
    @staticmethod
    def extract_dominant_colors(image_data, num_colors=3, focus_center=False):
        """
        Extract dominant colors, optionally focusing on the center region.

        Args:
        image_data (bytes): Raw image data
        num_colors (int): Number of dominant colors to extract
        focus_center (bool): If true, prioritize colors from the center region

        Returns:
        dict: Contains 'center_colors' and 'global_colors' lists
        """
        try:
            if focus_center:
                return {
                    'center_colors': ColorProcessor._extract_colors_opencv(image_data, num_colors, focus_center=True),
                    'global_colors': ColorProcessor._extract_colors_opencv(image_data, num_colors, focus_center=False)
                }
            else:
                return {
                    'global_colors': ColorProcessor._extract_colors_opencv(image_data, num_colors)
                }
        except ImportError:
            print("OpenCV not available; using fallback.")
            return [(255, 255, 255)] * num_colors  # Default to white

    @staticmethod
    def _extract_colors_opencv(image_data, num_colors, focus_center=False):
        """
        Extract dominant colors using OpenCV, optionally focusing on the center region.

        Args:
        image_data (bytes): Raw image data
        num_colors (int): Number of dominant colors to extract
        focus_center (bool): If true, extract from center region only

        Returns:
        list: List of RGB color tuples
        """
        import cv2

        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((100, 100))  # Resize for faster processing

        if focus_center:
            # Crop to center 50% of the image
            width, height = image.size
            left = width * 0.25
            top = height * 0.25
            right = width * 0.75
            bottom = height * 0.75
            image = image.crop((left, top, right, bottom))

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
    def is_color_displayable(color):
        """
        Check if the color can be displayed on an RGB strip.

        Args:
        color (tuple): RGB color values.

        Returns:
        bool: True if the color is displayable, False otherwise.
        """
        # Example criteria: Colors must have intensity values within 10-245 (to avoid extreme colors)
        min_intensity, max_intensity = 10, 245
        return all(min_intensity <= c <= max_intensity for c in color)

    @staticmethod
    def preview_colors(colors_dict):
        """
        Print a preview of colors in the terminal using ANSI escape sequences.

        Args:
        colors_dict (dict): Dictionary with 'center_colors' and/or 'global_colors' keys
        """
        if 'center_colors' in colors_dict:
            print("Center-Focused Colors:")
            for color in colors_dict['center_colors']:
                r, g, b = color
                ansi_color = f"\033[48;2;{r};{g};{b}m   \033[0m"
                print(f"{ansi_color} RGB: {color}")
            print()

        if 'global_colors' in colors_dict:
            print("Global Colors:")
            for color in colors_dict['global_colors']:
                r, g, b = color
                ansi_color = f"\033[48;2;{r};{g};{b}m   \033[0m"
                print(f"{ansi_color} RGB: {color}")
