"""
Generate beautiful images for LeetCode problems
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LeetCodeImageGenerator:
    """Creates styled images for LeetCode problems"""

    def __init__(self, output_dir: str = "generated_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Card dimensions
        self.width = 1200
        self.height = 630  # LinkedIn optimal size

        # Text colors (constant)
        self.text_color = (255, 255, 255)
        self.easy_color = (34, 197, 94)  # Green
        self.medium_color = (251, 191, 36)  # Yellow
        self.hard_color = (239, 68, 68)  # Red

    def _get_random_color_scheme(self):
        """Generate a random color scheme for the card"""
        import random

        # Dynamic color themes
        themes = [
            # Purple theme
            {'bg': (88, 28, 135), 'accent': (168, 85, 247), 'secondary': (216, 180, 254)},
            # Blue theme
            {'bg': (30, 58, 138), 'accent': (59, 130, 246), 'secondary': (147, 197, 253)},
            # Teal theme
            {'bg': (19, 78, 74), 'accent': (20, 184, 166), 'secondary': (153, 246, 228)},
            # Pink theme
            {'bg': (131, 24, 67), 'accent': (236, 72, 153), 'secondary': (249, 168, 212)},
            # Orange theme
            {'bg': (124, 45, 18), 'accent': (249, 115, 22), 'secondary': (253, 186, 116)},
            # Indigo theme
            {'bg': (49, 46, 129), 'accent': (99, 102, 241), 'secondary': (165, 180, 252)},
            # Rose theme
            {'bg': (136, 19, 55), 'accent': (244, 63, 94), 'secondary': (251, 207, 232)},
            # Cyan theme
            {'bg': (22, 78, 99), 'accent': (6, 182, 212), 'secondary': (165, 243, 252)},
        ]

        return random.choice(themes)

    def _get_font(self, size: int, bold: bool = False):
        """Get font with fallback to default"""
        try:
            if bold:
                return ImageFont.truetype("arialbd.ttf", size)
            return ImageFont.truetype("arial.ttf", size)
        except:
            # Fallback to default font
            return ImageFont.load_default()

    def generate_problem_image(
        self,
        problem: Dict,
        problem_details: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Generate a styled image for a LeetCode problem

        Args:
            problem: Basic problem info (id, title, slug)
            problem_details: Detailed info (content, difficulty, etc.) - optional

        Returns:
            Path to generated image
        """
        try:
            # Get random color scheme
            colors = self._get_random_color_scheme()
            bg_color = colors['bg']
            accent_color = colors['accent']
            secondary_color = colors['secondary']

            # Create image with gradient background
            img = Image.new('RGB', (self.width, self.height), bg_color)
            draw = ImageDraw.Draw(img)

            # Add gradient effect (simple vertical gradient)
            for y in range(self.height):
                alpha = y / self.height
                r = int(bg_color[0] * (1 - alpha) + 50 * alpha)
                g = int(bg_color[1] * (1 - alpha) + 20 * alpha)
                b = int(bg_color[2] * (1 - alpha) + 80 * alpha)
                draw.rectangle([(0, y), (self.width, y + 1)], fill=(r, g, b))

            # Fonts
            title_font = self._get_font(48, bold=True)
            number_font = self._get_font(36, bold=True)
            difficulty_font = self._get_font(28, bold=True)
            description_font = self._get_font(24)
            footer_font = self._get_font(20)

            # Draw LeetCode branding
            draw.text((60, 50), "LeetCode", font=title_font, fill=accent_color)

            # Draw problem number with badge
            problem_num = f"#{problem['id']}"
            draw.rounded_rectangle(
                [(60, 120), (180, 180)],
                radius=10,
                fill=accent_color
            )
            # Center the number in the badge
            bbox = draw.textbbox((0, 0), problem_num, font=number_font)
            num_width = bbox[2] - bbox[0]
            draw.text(
                (120 - num_width // 2, 130),
                problem_num,
                font=number_font,
                fill=self.text_color
            )

            # Draw difficulty badge
            difficulty = "Easy"  # Default
            diff_color = self.easy_color
            if problem_details:
                diff_level = problem_details.get('difficulty', 'Easy')
                if diff_level == 'Medium':
                    difficulty = 'Medium'
                    diff_color = self.medium_color
                elif diff_level == 'Hard':
                    difficulty = 'Hard'
                    diff_color = self.hard_color

            draw.rounded_rectangle(
                [(200, 130), (320, 170)],
                radius=10,
                fill=diff_color
            )
            draw.text((220, 135), difficulty, font=difficulty_font, fill=(0, 0, 0))

            # Draw acceptance rate if available
            if 'acceptance_rate' in problem:
                rate_text = f"{problem['acceptance_rate']:.0f}% ✓"
                draw.text((340, 138), rate_text, font=difficulty_font, fill=secondary_color)

            # Draw problem title (wrapped to 2 lines max)
            title = problem['title']
            title_wrapped = textwrap.fill(title, width=35)
            title_lines = title_wrapped.split('\n')[:2]  # Max 2 lines

            title_y = 240
            for line in title_lines:
                # Shadow for depth
                draw.text((62, title_y + 2), line, font=title_font, fill=(0, 0, 0, 100))
                # Main text
                draw.text((60, title_y), line, font=title_font, fill=self.text_color)
                title_y += 55

            # Draw FULL problem description if available
            if problem_details and problem_details.get('content'):
                import re
                content = problem_details['content']
                # Remove HTML tags
                content = re.sub(r'<[^>]+>', ' ', content)
                # Clean up extra whitespace
                content = re.sub(r'\s+', ' ', content).strip()

                # Wrap the FULL description (not just first sentence)
                # Use smaller font to fit more text
                desc_font = self._get_font(20)
                wrapped_desc = textwrap.fill(content, width=95)
                desc_y = title_y + 20
                max_desc_y = self.height - 100  # Leave room for footer

                for line in wrapped_desc.split('\n'):
                    if desc_y > max_desc_y:
                        # Add "..." if we run out of space
                        draw.text((60, desc_y - 10), "...", font=desc_font, fill=secondary_color)
                        break
                    draw.text((60, desc_y), line, font=desc_font, fill=secondary_color)
                    desc_y += 26

            # Draw footer
            footer_y = self.height - 60
            draw.text(
                (60, footer_y),
                "💡 Tap to see the solution approach!",
                font=footer_font,
                fill=secondary_color
            )

            # Draw decorative accent line
            draw.rectangle(
                [(0, self.height - 10), (self.width, self.height)],
                fill=accent_color
            )

            # Save image
            filename = f"leetcode_{problem['id']}_{problem['slug'][:30]}.png"
            filepath = self.output_dir / filename
            img.save(filepath, 'PNG', quality=95)

            logger.info(f"Generated LeetCode image: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error generating LeetCode image: {str(e)}")
            return None


if __name__ == "__main__":
    # Test the generator
    logging.basicConfig(level=logging.INFO)
    generator = LeetCodeImageGenerator()

    test_problem = {
        'id': 1,
        'title': 'Two Sum',
        'slug': 'two-sum',
        'acceptance_rate': 49.5
    }

    test_details = {
        'difficulty': 'Easy',
        'content': '<p>Given an array of integers <code>nums</code> and an integer <code>target</code>, return indices of the two numbers such that they add up to <code>target</code>.</p>'
    }

    image_path = generator.generate_problem_image(test_problem, test_details)
    if image_path:
        print(f"✓ Test image generated: {image_path}")
