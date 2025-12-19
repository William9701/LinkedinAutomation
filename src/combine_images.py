"""
Combine two images vertically into one
"""
from PIL import Image
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def combine_images_vertical(image1_path: str, image2_path: str, output_path: str = None) -> str:
    """
    Combine two images vertically (image1 on top, image2 on bottom)

    Args:
        image1_path: Path to first image (question)
        image2_path: Path to second image (code)
        output_path: Optional output path

    Returns:
        Path to combined image
    """
    try:
        # Open images
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)

        # Get dimensions
        width = max(img1.width, img2.width)
        total_height = img1.height + img2.height

        # Create new image
        combined = Image.new('RGB', (width, total_height))

        # Paste images
        combined.paste(img1, (0, 0))
        combined.paste(img2, (0, img1.height))

        # Save
        if not output_path:
            output_path = str(Path(image1_path).parent / "combined_leetcode.png")

        combined.save(output_path, 'PNG', quality=95)
        logger.info(f"Combined images saved to: {output_path}")

        return output_path

    except Exception as e:
        logger.error(f"Error combining images: {str(e)}")
        return None
