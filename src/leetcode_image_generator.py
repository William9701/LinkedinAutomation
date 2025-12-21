"""
Generate beautiful images for LeetCode problems
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap
import re
import random
import html
from pathlib import Path
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LeetCodeImageGenerator:
    """Creates styled images for LeetCode problems"""

    def __init__(self, output_dir: str = "generated_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Card dimensions - Increased by 10% (5% left, 5% right)
        self.initial_width = 1540  # 1400 * 1.10 = 1540
        self.initial_height = 800  # Taller for more content

        # Text colors (constant)
        self.text_color = (255, 255, 255)
        self.easy_color = (34, 197, 94)  # Green
        self.medium_color = (251, 191, 36)  # Yellow
        self.hard_color = (239, 68, 68)  # Red

    def _get_random_color_scheme(self):
        """Generate a random color scheme for the card"""
        # Dynamic color themes - Brighter with better contrast
        themes = [
            # Bright Purple theme
            {'bg': (75, 0, 130), 'accent': (186, 85, 211), 'secondary': (240, 230, 255)},
            # Bright Blue theme
            {'bg': (0, 51, 153), 'accent': (30, 144, 255), 'secondary': (240, 248, 255)},
            # Bright Teal theme
            {'bg': (0, 102, 102), 'accent': (0, 206, 209), 'secondary': (240, 255, 255)},
            # Bright Pink theme
            {'bg': (153, 0, 76), 'accent': (255, 20, 147), 'secondary': (255, 240, 245)},
            # Bright Orange theme
            {'bg': (153, 51, 0), 'accent': (255, 140, 0), 'secondary': (255, 250, 240)},
            # Bright Indigo theme
            {'bg': (51, 0, 153), 'accent': (138, 43, 226), 'secondary': (248, 240, 255)},
            # Bright Rose theme
            {'bg': (153, 0, 51), 'accent': (255, 0, 127), 'secondary': (255, 240, 245)},
            # Bright Cyan theme
            {'bg': (0, 102, 153), 'accent': (0, 191, 255), 'secondary': (240, 255, 255)},
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

            # Calculate dynamic width based on content
            if problem_details and problem_details.get('content'):
                content = re.sub(r'<[^>]+>', ' ', problem_details['content'])
                content = re.sub(r'\s+', ' ', content).strip()
                # Estimate width needed (rough estimate: ~11px per char at font size 28)
                max_line_len = max(len(line) for line in textwrap.wrap(content, width=80))
                calculated_width = max(self.initial_width, (max_line_len * 14) + 120)
            else:
                calculated_width = self.initial_width

            final_width = calculated_width
            final_height = self.initial_height

            # Create image with gradient background
            img = Image.new('RGB', (final_width, final_height), bg_color)
            draw = ImageDraw.Draw(img)

            # Add gradient effect (simple vertical gradient)
            for y in range(final_height):
                alpha = y / final_height
                r = int(bg_color[0] * (1 - alpha) + 50 * alpha)
                g = int(bg_color[1] * (1 - alpha) + 20 * alpha)
                b = int(bg_color[2] * (1 - alpha) + 80 * alpha)
                draw.rectangle([(0, y), (final_width, y + 1)], fill=(r, g, b))

            # Fonts - Increased for better visibility
            title_font = self._get_font(60, bold=True)
            number_font = self._get_font(48, bold=True)
            difficulty_font = self._get_font(38, bold=True)
            description_font = self._get_font(32)  # Increased from 28 to 32
            footer_font = self._get_font(24)

            # Draw LeetCode branding
            draw.text((60, 50), "LeetCode", font=title_font, fill=accent_color)

            # Draw problem number with badge (dark semi-transparent background)
            problem_num = f"#{problem['id']}"
            # Calculate badge size based on text
            bbox = draw.textbbox((0, 0), problem_num, font=number_font)
            num_width = bbox[2] - bbox[0]
            num_height = bbox[3] - bbox[1]

            # Draw dark badge background
            badge_padding = 15
            draw.rounded_rectangle(
                [(50, 115), (50 + num_width + badge_padding * 2, 115 + num_height + badge_padding * 2)],
                radius=10,
                fill=(0, 0, 0, 150)  # Semi-transparent black
            )
            # Draw number in the badge
            draw.text(
                (50 + badge_padding, 120),
                problem_num,
                font=number_font,
                fill=accent_color  # Use accent color for visibility
            )

            # Draw difficulty badge - moved down to align better
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
                [(200, 138), (320, 178)],  # Moved down by 8px
                radius=10,
                fill=diff_color
            )
            draw.text((220, 143), difficulty, font=difficulty_font, fill=(0, 0, 0))  # Moved down by 8px

            # Draw acceptance rate if available
            if 'acceptance_rate' in problem:
                rate_text = f"{problem['acceptance_rate']:.0f}%"
                draw.text((340, 146), rate_text, font=difficulty_font, fill=secondary_color)  # Moved down by 8px

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

            # Draw problem description if available (stop before examples)
            if problem_details and problem_details.get('content'):
                content = problem_details['content']

                # Parse HTML content properly
                # First decode HTML entities
                content = html.unescape(content)

                # STOP at "Example" section - try multiple patterns
                if '<strong>Example' in content:
                    content = content.split('<strong>Example')[0]
                elif 'Example 1' in content:
                    content = content.split('Example 1')[0]
                elif 'Example' in content:
                    # Find first occurrence of Example followed by number/colon
                    match = re.search(r'Example\s*\d*\s*:', content, re.IGNORECASE)
                    if match:
                        content = content[:match.start()]

                # Replace common HTML tags with formatting
                content = re.sub(r'<p>', '\n\n', content)
                content = re.sub(r'</p>', '', content)
                content = re.sub(r'<ul>', '\n', content)
                content = re.sub(r'</ul>', '\n', content)
                content = re.sub(r'<li>', '\n• ', content)
                content = re.sub(r'</li>', '', content)
                content = re.sub(r'<strong>|<b>', '', content)
                content = re.sub(r'</strong>|</b>', '', content)
                content = re.sub(r'<code>', '', content)
                content = re.sub(r'</code>', '', content)
                content = re.sub(r'<pre>', '\n', content)
                content = re.sub(r'</pre>', '\n', content)

                # Remove any remaining HTML tags
                content = re.sub(r'<[^>]+>', '', content)

                # Clean up extra whitespace but preserve paragraph breaks
                content = re.sub(r' +', ' ', content)
                content = re.sub(r'\n\n+', '\n\n', content)
                content = content.strip()

                # Larger font for better visibility
                desc_font = self._get_font(32, bold=False)

                # Count lines needed for dynamic height
                lines_list = []
                for paragraph in content.split('\n\n'):
                    if paragraph.strip():
                        wrapped = textwrap.fill(paragraph.strip(), width=50)
                        lines_list.extend(wrapped.split('\n'))
                        lines_list.append('')  # Add spacing between paragraphs

                # Calculate required height
                line_height = 40
                content_height = len(lines_list) * line_height + 300  # Add padding
                final_height = max(final_height, content_height)

                # Recreate image with new height
                img = Image.new('RGB', (final_width, final_height), bg_color)
                draw = ImageDraw.Draw(img)

                # Add gradient effect
                for y in range(final_height):
                    alpha = y / final_height
                    r = int(bg_color[0] * (1 - alpha) + 50 * alpha)
                    g = int(bg_color[1] * (1 - alpha) + 20 * alpha)
                    b = int(bg_color[2] * (1 - alpha) + 80 * alpha)
                    draw.rectangle([(0, y), (final_width, y + 1)], fill=(r, g, b))

                # Redraw header (LeetCode branding)
                header_font = self._get_font(60, bold=True)
                number_font = self._get_font(48, bold=True)
                difficulty_font = self._get_font(38, bold=True)
                footer_font = self._get_font(24)

                draw.text((60, 50), "LeetCode", font=header_font, fill=accent_color)

                # Redraw problem number and stats
                problem_num = f"#{problem['id']}"
                draw.text((60, 120), problem_num, font=number_font, fill=accent_color)

                difficulty = problem_details.get('difficulty', 'Medium') if problem_details else 'Medium'
                diff_color = {
                    'Easy': self.easy_color,
                    'Medium': self.medium_color,
                    'Hard': self.hard_color
                }.get(difficulty, self.medium_color)

                diff_bbox = draw.textbbox((0, 0), difficulty, font=difficulty_font)
                diff_width = diff_bbox[2] - diff_bbox[0]
                diff_height = diff_bbox[3] - diff_bbox[1]

                diff_x = 250
                diff_y = 100
                padding = 15
                draw.rounded_rectangle(
                    [(diff_x - padding, diff_y - padding//2),
                     (diff_x + diff_width + padding, diff_y + diff_height + padding)],
                    radius=8,
                    fill=diff_color
                )
                draw.text((diff_x, diff_y), difficulty, font=difficulty_font, fill=(20, 20, 35))

                acceptance_rate = problem_details.get('acceptance_rate', '0%') if problem_details else '0%'
                draw.text((diff_x + diff_width + 60, 105), acceptance_rate, font=self._get_font(48), fill=self.text_color)

                # Redraw title
                title_y = 180
                for line in title_lines:
                    draw.text((62, title_y + 2), line, font=title_font, fill=(0, 0, 0, 100))
                    draw.text((60, title_y), line, font=title_font, fill=self.text_color)
                    title_y += 55

                # Draw formatted description
                desc_y = title_y + 30
                for line in lines_list:
                    if line:  # Non-empty line
                        draw.text((60, desc_y), line, font=desc_font, fill=secondary_color)
                    desc_y += line_height

            # Draw footer
            footer_y = final_height - 60
            draw.text(
                (60, footer_y),
                "💡 Tap to see the solution approach!",
                font=footer_font,
                fill=secondary_color
            )

            # Draw decorative accent line
            draw.rectangle(
                [(0, final_height - 10), (final_width, final_height)],
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
