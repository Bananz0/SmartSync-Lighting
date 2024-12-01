import numpy as np
from PIL import Image
import io


class ColorProcessor:
    DEBUG = False  # Enable or disable debug logs

    @staticmethod
    def extract_dominant_colors(image_data, num_colors=3, focus_percentage=50):
        """
        Extract dominant colors, blending center and global colors based on focus percentage.

        Args:
            image_data (bytes): Raw image data.
            num_colors (int): Number of dominant colors to extract.
            focus_percentage (int): Percentage (0-100) of importance to center-focused colors.

        Returns:
            dict: Contains 'blended_colors' list with dynamically weighted colors.
        """
        try:
            # Extract center and global colors separately
            center_colors = ColorProcessor._extract_colors_opencv(image_data, num_colors, focus_center=True)
            global_colors = ColorProcessor._extract_colors_opencv(image_data, num_colors, focus_center=False)

            # Calculate weights for blending
            center_weight = focus_percentage / 100
            global_weight = 1 - center_weight

            # Blend the colors dynamically based on weights
            blended_colors = ColorProcessor._blend_colors(center_colors, global_colors, center_weight, global_weight)

            return {
                'center_colors': center_colors,
                'global_colors': global_colors,
                'blended_colors': blended_colors
            }
        except ImportError:
            print("OpenCV not available; using fallback.")
            return {'blended_colors': [(255, 255, 255)] * num_colors}  # Default to white

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

    @staticmethod
    def _blend_colors(center_colors, global_colors, center_weight, global_weight):
        """
        Blend center and global colors based on specified weights.

        Args:
            center_colors (list): List of center-focused RGB colors.
            global_colors (list): List of globally extracted RGB colors.
            center_weight (float): Weight (0-1) for center colors.
            global_weight (float): Weight (0-1) for global colors.

        Returns:
            list: Blended list of RGB colors.
        """
        blended_colors = []

        # Adjust weights to determine number of colors from each list
        num_center_colors = round(center_weight * len(center_colors))
        num_global_colors = round(global_weight * len(global_colors))

        # Take weighted samples
        blended_colors.extend(center_colors[:num_center_colors])
        blended_colors.extend(global_colors[:num_global_colors])

        # Remove duplicates while preserving order
        seen = set()
        unique_colors = [c for c in blended_colors if not (c in seen or seen.add(c))]

        return unique_colors
