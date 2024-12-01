import unittest
from src.core.color_processor import ColorProcessor
from PIL import Image
import io

class TestColorProcessor(unittest.TestCase):

    def test_is_color_displayable_valid(self):
        self.assertTrue(ColorProcessor.is_color_displayable((100, 150, 200)))

    def test_is_color_displayable_invalid(self):
        self.assertFalse(ColorProcessor.is_color_displayable((255, 255, 255)))  # Too bright
        self.assertFalse(ColorProcessor.is_color_displayable((0, 0, 0)))  # Too dark

    def test_normalize_color(self):
        color = (128, 64, 32)
        normalized = ColorProcessor.normalize_color(color)
        self.assertEqual(normalized, (0.5019607843137255, 0.25098039215686274, 0.12549019607843137))

    def test_extract_dominant_colors(self):
        # Create a simple test image in memory
        image = Image.new("RGB", (100, 100), (128, 128, 128))  # A solid gray image
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()

        # Pass valid image data to the function
        try:
            colors = ColorProcessor.extract_dominant_colors(img_bytes, num_colors=3)

            # Ensure the returned colors are valid
            self.assertGreaterEqual(len(colors), 1)  # At least 1 color should be returned
            self.assertLessEqual(len(colors), 3)  # No more than the requested number of colors
        except Exception:
            self.fail("extract_dominant_colors raised an exception unexpectedly!")


if __name__ == "__main__":
    unittest.main()
