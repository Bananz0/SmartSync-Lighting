import numpy as np
from PIL import Image
import io


class ColorProcessor:
    DEBUG = False  # Enable or disable debug logs

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
            return {'global_colors': [(255, 255, 255)] * num_colors}  # Default to white

    @staticmethod
    def _extract_colors_opencv(image_data, num_colors, focus_center=False):
        """
        Extract dominant colors using OpenCV, optionally focusing on the center region.

        Args:
            image_data (bytes): Raw image data.
            num_colors (int): Number of dominant colors to extract.
            focus_center (bool): If true, extract from center region only.

        Returns:
            list: List of RGB color tuples.
        """
        import cv2
        import numpy as np
        from PIL import Image
        import io

        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        image = image.resize((100, 100))  # Resize for faster processing

        if focus_center:
            # Crop to center 50% of the image
            width, height = image.size
            left = width * 0.25
            top = height * 0.25
            right = width * 0.75
            bottom = height * 0.75
            image = image.crop((left, top, right, bottom))

        # Convert image to numpy array
        np_image = np.array(image)
        pixels = np_image.reshape((-1, 3))
        pixels = np.float32(pixels)

        # Ensure the array has the correct dimensions
        if len(pixels) == 0 or pixels.shape[1] != 3:
            raise ValueError("Unexpected array shape during color extraction.")

        # Perform k-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        flags = cv2.KMEANS_RANDOM_CENTERS

        _, labels, centers = cv2.kmeans(pixels, num_colors * 2, None, criteria, 10, flags)

        # Count points in each cluster
        _, counts = np.unique(labels, return_counts=True)

        # Sort clusters by size
        sorted_indices = np.argsort(-counts)
        sorted_colors = [tuple(map(int, centers[i])) for i in sorted_indices]

        # Filter out dark colors
        filtered_colors = [color for color in sorted_colors if not ColorProcessor.is_color_too_dark(color)]

        # If not enough colors, adjust num_colors
        if len(filtered_colors) < num_colors:
            num_colors = len(filtered_colors)

        return filtered_colors[:num_colors]

    @staticmethod
    def is_color_too_dark(color, threshold=30):
        """
        Determine if a color is too dark (e.g., black).

        Args:
            color (tuple): RGB color.
            threshold (int): Maximum average intensity below which the color is considered too dark.

        Returns:
            bool: True if the color is too dark, False otherwise.
        """
        return sum(color) / 3 < threshold

    @staticmethod
    def normalize_color(color):
        """
        Normalize RGB color from 0-255 range to 0-1 range.

        Args:
            color (tuple): RGB color values (0-255 range).

        Returns:
            tuple: Normalized RGB color (0-1 range).
        """
        normalized = tuple(c / 255.0 for c in color)
        if ColorProcessor.DEBUG:
            print(f"Normalizing color {color} to {normalized}")
        return normalized

    @staticmethod
    def is_color_displayable(color):
        """
        Check if the color can be displayed on an RGB strip.

        Args:
            color (tuple): RGB color values (0-255 range).

        Returns:
            bool: True if the color is displayable, False otherwise.
        """
        # Exclude colors that are too dark or too light
        min_intensity, max_intensity = 20, 235
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
