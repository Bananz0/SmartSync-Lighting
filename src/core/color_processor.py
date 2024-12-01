import numpy as np
from PIL import Image
import io


class ColorProcessor:
    @staticmethod
    def extract_dominant_color(image_data):
        """
        Extract dominant color from image data using k-means clustering

        Args:
        image_data (bytes): Raw image data

        Returns:
        tuple: RGB color values
        """
        if not image_data:
            return (255, 255, 255)  # Default white

        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Resize image for faster processing
            image = image.resize((100, 100))

            # Convert image to numpy array
            np_image = np.array(image)

            # Reshape the image to be a list of pixels
            pixels = np_image.reshape((-1, 3))

            # Convert to float
            pixels = np.float32(pixels)

            # Define criteria, number of clusters(K) and apply kmeans()
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            flags = cv2.KMEANS_RANDOM_CENTERS

            # Apply K-Means
            k = 3
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, flags)

            # Count points in each cluster
            _, counts = np.unique(labels, return_counts=True)

            # Find the dominant color (cluster with most points)
            dominant_color_index = np.argmax(counts)
            dominant_color = centers[dominant_color_index]

            # Convert to integer RGB
            return tuple(map(int, dominant_color))

        except Exception as e:
            print(f"Error extracting dominant color: {e}")
            return (255, 255, 255)  # Default white

    @staticmethod
    def normalize_color(color, max_intensity=255):
        """
        Normalize color to a 0-1 range

        Args:
        color (tuple): RGB color values
        max_intensity (int): Maximum color intensity

        Returns:
        tuple: Normalized RGB color values
        """
        return tuple(c / max_intensity for c in color)