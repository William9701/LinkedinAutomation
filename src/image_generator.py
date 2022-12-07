import requests
import logging
from pathlib import Path
from typing import Optional
import time

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generates images for LinkedIn posts - supports multiple providers"""

    def __init__(self, openai_api_key: Optional[str] = None, replicate_token: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.replicate_token = replicate_token
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)

    def generate_image(self, prompt: str, filename: str = None) -> Optional[str]:
        """
        Generate an image from a text prompt

        Args:
            prompt: Image generation prompt
            filename: Optional filename (without extension)

        Returns:
            Path to generated image or None if generation failed
        """
        if not filename:
            filename = f"post_image_{int(time.time())}"

        # Try OpenAI DALL-E first if API key is available
        if self.openai_api_key:
            image_path = self._generate_with_dalle(prompt, filename)
            if image_path:
                return image_path

        # Try Replicate (Stable Diffusion) if token is available
        if self.replicate_token:
            image_path = self._generate_with_replicate(prompt, filename)
            if image_path:
                return image_path

        # If no API keys or both failed, return None
        logger.warning("No image generation API keys configured or all attempts failed")
        return None

    def _generate_with_dalle(self, prompt: str, filename: str) -> Optional[str]:
        """Generate image using OpenAI DALL-E"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            # Enhance prompt for professional LinkedIn image
            enhanced_prompt = f"Professional, clean, modern technical illustration: {prompt}. Minimalist design, corporate color scheme, no text, suitable for LinkedIn post."

            response = client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Download and save the image
            image_response = requests.get(image_url, timeout=30)
            if image_response.status_code == 200:
                image_path = self.output_dir / f"{filename}.png"
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                logger.info(f"Image generated successfully with DALL-E: {image_path}")
                return str(image_path)

        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {str(e)}")

        return None

    def _generate_with_replicate(self, prompt: str, filename: str) -> Optional[str]:
        """Generate image using Replicate (Stable Diffusion)"""
        try:
            import replicate

            # Enhance prompt for professional LinkedIn image
            enhanced_prompt = f"Professional technical illustration, {prompt}, minimalist, clean design, corporate colors, high quality, no text"

            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": enhanced_prompt,
                    "negative_prompt": "ugly, blurry, low quality, text, watermark, people, faces, stock photo",
                    "width": 1024,
                    "height": 1024,
                }
            )

            if output and len(output) > 0:
                image_url = output[0]
                # Download and save the image
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code == 200:
                    image_path = self.output_dir / f"{filename}.png"
                    with open(image_path, 'wb') as f:
                        f.write(image_response.content)
                    logger.info(f"Image generated successfully with Replicate: {image_path}")
                    return str(image_path)

        except Exception as e:
            logger.error(f"Error generating image with Replicate: {str(e)}")

        return None

    def create_simple_placeholder(self, text: str, filename: str) -> str:
        """
        Create a simple placeholder image with text (fallback option)
        Requires PIL/Pillow
        """
        try:
            from PIL import Image, ImageDraw, ImageFont

            # Create a simple colored background
            img = Image.new('RGB', (1200, 630), color=(41, 98, 255))  # LinkedIn blue
            draw = ImageDraw.Draw(img)

            # Try to use a nice font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()

            # Add text
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            position = ((1200 - text_width) / 2, (630 - text_height) / 2)

            draw.text(position, text, fill=(255, 255, 255), font=font)

            # Save
            image_path = self.output_dir / f"{filename}.png"
            img.save(image_path)
            logger.info(f"Placeholder image created: {image_path}")
            return str(image_path)

        except Exception as e:
            logger.error(f"Error creating placeholder image: {str(e)}")
            return None
