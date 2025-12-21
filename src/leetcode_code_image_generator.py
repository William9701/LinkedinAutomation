"""
Generate beautiful code solution images with Python and TypeScript side-by-side
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import logging
import random
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LeetCodeCodeImageGenerator:
    """Creates styled images showing code solutions in Python and TypeScript"""

    def __init__(self, output_dir: str = "generated_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Card dimensions - Wider for side-by-side layout (10% increase = 3080)
        self.width = 3080  # 2800 * 1.10 = 3080
        self.height = 1200

        # Text colors
        self.text_color = (255, 255, 255)
        self.comment_color = (34, 197, 94)  # GREEN for comments
        self.function_color = (255, 215, 0)  # YELLOW for function names
        self.return_color = (200, 100, 255)  # PURPLE for return statements
        self.border_color = (200, 200, 200)  # Lighter gray border

    def _get_random_color_scheme(self):
        """Generate a random color scheme for the card - VERY DARK backgrounds"""
        # Very dark themes for solution/code display
        themes = [
            # Very Dark Purple
            {'bg': (15, 5, 25), 'accent': (186, 85, 211), 'secondary': (200, 180, 220)},
            # Very Dark Blue
            {'bg': (5, 10, 30), 'accent': (100, 180, 255), 'secondary': (180, 200, 255)},
            # Very Dark Teal
            {'bg': (5, 20, 25), 'accent': (80, 200, 210), 'secondary': (180, 230, 235)},
            # Very Dark Magenta
            {'bg': (25, 5, 20), 'accent': (255, 100, 200), 'secondary': (255, 180, 220)},
            # Very Dark Red
            {'bg': (25, 10, 10), 'accent': (255, 120, 80), 'secondary': (255, 200, 180)},
            # Very Dark Indigo
            {'bg': (10, 5, 30), 'accent': (160, 100, 255), 'secondary': (200, 180, 255)},
            # Very Dark Green
            {'bg': (5, 20, 15), 'accent': (100, 220, 150), 'secondary': (180, 255, 200)},
            # Very Dark Navy
            {'bg': (8, 12, 25), 'accent': (100, 180, 255), 'secondary': (180, 210, 255)},
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

    def generate_code_solution_image(
        self,
        problem: Dict,
        python_code: str,
        typescript_code: str
    ) -> Optional[str]:
        """
        Generate side-by-side code image

        Args:
            problem: Basic problem info (id, title)
            python_code: Python solution with comments
            typescript_code: TypeScript solution with comments

        Returns:
            Path to generated image
        """
        try:
            # Get random color scheme (same as question)
            colors = self._get_random_color_scheme()
            bg_color = colors['bg']
            accent_color = colors['accent']
            secondary_color = colors['secondary']

            # Calculate dynamic height based on code length
            line_height = 65  # Increased for larger font (52)

            # Calculate max chars that can fit (same calculation as in rendering)
            middle_x = self.width // 2
            left_margin = 60
            available_width = middle_x - left_margin - 20  # Minimal padding
            char_width = 31  # Adjusted for font size 52 (was 28 for 48)
            max_width_chars = int(available_width / char_width)

            # Count lines needed for Python (word-based wrapping)
            python_lines = 0
            for line in python_code.split('\n'):
                if len(line) > max_width_chars:
                    words = line.split(' ')
                    current_len = 0
                    line_count = 1
                    for word in words:
                        test_len = current_len + len(word) + (1 if current_len > 0 else 0)
                        if test_len <= max_width_chars:
                            current_len = test_len
                        else:
                            line_count += 1
                            current_len = len(word)
                    python_lines += line_count
                else:
                    python_lines += 1

            # Count lines needed for TypeScript (word-based wrapping)
            ts_lines = 0
            for line in typescript_code.split('\n'):
                if len(line) > max_width_chars:
                    words = line.split(' ')
                    current_len = 0
                    line_count = 1
                    for word in words:
                        test_len = current_len + len(word) + (1 if current_len > 0 else 0)
                        if test_len <= max_width_chars:
                            current_len = test_len
                        else:
                            line_count += 1
                            current_len = len(word)
                    ts_lines += line_count
                else:
                    ts_lines += 1

            # Use the maximum of both
            max_lines = max(python_lines, ts_lines)
            dynamic_height = 260 + (max_lines * line_height) + 100  # header + content + footer
            final_height = max(self.height, dynamic_height)

            # Create image with gradient background (same as question)
            img = Image.new('RGB', (self.width, final_height), bg_color)
            draw = ImageDraw.Draw(img)

            # Add black gradient effect (gradient from accent color to black)
            for y in range(final_height):
                alpha = y / final_height
                # Gradient from top color to pure black at bottom
                r = int(bg_color[0] * (1 - alpha))
                g = int(bg_color[1] * (1 - alpha))
                b = int(bg_color[2] * (1 - alpha))
                draw.rectangle([(0, y), (self.width, y + 1)], fill=(r, g, b))

            # Fonts - Increased for better readability
            title_font = self._get_font(60, bold=True)
            code_font = self._get_font(52)  # Increased from 48 to 52
            label_font = self._get_font(48, bold=True)

            # Draw title at top
            draw.text((60, 50), "Solution", font=title_font, fill=accent_color)

            # Draw problem number
            problem_num = f"#{problem['id']}"
            draw.text((60, 120), problem_num, font=label_font, fill=accent_color)

            # Draw vertical border line in the middle
            middle_x = self.width // 2
            draw.line([(middle_x, 180), (middle_x, final_height - 20)], fill=self.border_color, width=3)

            # Left side: Python
            draw.text((60, 200), "PYTHON", font=label_font, fill=secondary_color)

            # Draw Python code with wrapping
            python_y = 260
            left_margin = 60
            # Calculate max chars based on available width
            # Available width = (middle_x - left_margin - padding) / char_width
            # For font size 52, approximate char width is 31px
            available_width = middle_x - left_margin - 20  # Minimal 20px padding from border
            char_width = 31  # Adjusted for font size 52
            max_width_chars = int(available_width / char_width)

            for line in python_code.split('\n'):
                # Green for comments, yellow for function definitions, purple for return
                is_comment = line.strip().startswith('#')
                is_function = line.strip().startswith('def ')
                is_return = line.strip().startswith('return ')

                if is_comment:
                    line_color = self.comment_color
                elif is_function:
                    line_color = self.function_color
                elif is_return:
                    line_color = self.return_color
                else:
                    line_color = self.text_color

                # Wrap long lines - WORD-BASED wrapping (don't break words)
                if len(line) > max_width_chars:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) <= max_width_chars:
                            current_line = test_line
                        else:
                            # Draw current line and start new one
                            if current_line:
                                draw.text((left_margin, python_y), current_line, font=code_font, fill=line_color)
                                python_y += 65
                            current_line = word
                    # Draw remaining text
                    if current_line:
                        draw.text((left_margin, python_y), current_line, font=code_font, fill=line_color)
                        python_y += 65
                else:
                    draw.text((left_margin, python_y), line, font=code_font, fill=line_color)
                    python_y += 65  # Increased line height

            # Right side: TypeScript
            right_margin = middle_x + 60
            draw.text((right_margin, 200), "TYPESCRIPT", font=label_font, fill=secondary_color)

            # Draw TypeScript code with wrapping
            ts_y = 260
            for line in typescript_code.split('\n'):
                # Green for comments, yellow for function definitions, purple for return
                is_comment = line.strip().startswith('//')
                is_function = line.strip().startswith('function ')
                is_return = line.strip().startswith('return ')

                if is_comment:
                    line_color = self.comment_color
                elif is_function:
                    line_color = self.function_color
                elif is_return:
                    line_color = self.return_color
                else:
                    line_color = self.text_color

                # Wrap long lines - WORD-BASED wrapping (don't break words)
                if len(line) > max_width_chars:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) <= max_width_chars:
                            current_line = test_line
                        else:
                            # Draw current line and start new one
                            if current_line:
                                draw.text((right_margin, ts_y), current_line, font=code_font, fill=line_color)
                                ts_y += 65
                            current_line = word
                    # Draw remaining text
                    if current_line:
                        draw.text((right_margin, ts_y), current_line, font=code_font, fill=line_color)
                        ts_y += 65
                else:
                    draw.text((right_margin, ts_y), line, font=code_font, fill=line_color)
                    ts_y += 65  # Increased line height

            # Draw decorative accent line at bottom
            draw.rectangle(
                [(0, final_height - 10), (self.width, final_height)],
                fill=accent_color
            )

            # Save image
            filename = f"leetcode_{problem['id']}_solution.png"
            filepath = self.output_dir / filename
            img.save(filepath, 'PNG', quality=95)

            logger.info(f"Generated code solution image: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error generating code image: {str(e)}")
            return None


if __name__ == "__main__":
    # Test with sample
    logging.basicConfig(level=logging.INFO)
    generator = LeetCodeCodeImageGenerator()

    test_problem = {'id': 1, 'title': 'Two Sum'}

    python_code = """def twoSum(nums, target):
    # Store seen numbers
    seen = {}

    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

    return []"""

    typescript_code = """function twoSum(nums: number[], target: number): number[] {
    // Store seen numbers
    const seen = new Map<number, number>();

    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (seen.has(complement)) {
            return [seen.get(complement)!, i];
        }
        seen.set(nums[i], i);
    }

    return [];
}"""

    result = generator.generate_code_solution_image(test_problem, python_code, typescript_code)
    if result:
        print(f"✓ Test image generated: {result}")
