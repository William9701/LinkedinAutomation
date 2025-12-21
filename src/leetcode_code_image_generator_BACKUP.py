"""
Generate beautiful code solution images with Python and TypeScript side-by-side
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LeetCodeCodeImageGenerator:
    """Creates styled images showing code solutions in Python and TypeScript"""

    def __init__(self, output_dir: str = "generated_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Card dimensions - Dynamic based on content
        self.initial_width = 1400  # Starting width, will expand if needed
        self.initial_height = 1200  # Starting height, will expand if needed

        # Colors - Bright and highly visible
        self.bg_color = (20, 20, 35)  # Dark blue-black background
        self.text_color = (255, 255, 255)  # Pure white text for maximum visibility
        self.comment_color = (144, 238, 144)  # Bright light green for comments
        self.keyword_color = (86, 156, 214)  # Blue for keywords
        self.string_color = (206, 145, 120)  # Orange for strings
        self.divider_color = (100, 100, 100)  # Gray divider
        self.header_color = (255, 215, 0)  # Bright gold for headers

    def _get_font(self, size: int, bold: bool = False):
        """Get font with fallback"""
        try:
            if bold:
                return ImageFont.truetype("consola.ttf", size)  # Consolas for code
            return ImageFont.truetype("consola.ttf", size)
        except:
            try:
                return ImageFont.truetype("cour.ttf", size)  # Courier fallback
            except:
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
            # Fonts - Larger to match question image readability (monospace needs bigger size)
            header_font = self._get_font(84, bold=True)
            code_font = self._get_font(48)

            # FIRST PASS: Calculate required dimensions
            barrier_width = 20

            # Find the longest line in both Python and TypeScript to calculate width
            max_python_len = max(len(line) for line in python_code.split('\n')) if python_code else 0
            max_ts_len = max(len(line) for line in typescript_code.split('\n')) if typescript_code else 0
            max_code_len = max(max_python_len, max_ts_len)

            # Calculate width needed (each side needs to fit the longest line)
            # Character width ~30px for font size 48, add padding and barrier
            chars_per_side = max_code_len
            side_width = max(1200, (chars_per_side * 30) + 240)  # Min 1200px per side
            calculated_width = (side_width * 2) + barrier_width + 80
            final_width = max(self.initial_width, calculated_width)

            middle_x = final_width // 2

            # Adjust max_line_width based on available space (no wrapping needed now)
            max_line_width = 200  # Much higher limit, let text flow naturally

            # Count Python lines (with wrapping)
            python_lines = 0
            for line in python_code.split('\n'):
                if len(line) <= max_line_width:
                    python_lines += 1
                else:
                    # Count wrapped lines
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) <= max_line_width:
                            current_line = test_line
                        else:
                            if current_line:
                                python_lines += 1
                            current_line = word
                    if current_line:
                        python_lines += 1

            # Count TypeScript lines (with wrapping)
            ts_lines = 0
            for line in typescript_code.split('\n'):
                if len(line) <= max_line_width:
                    ts_lines += 1
                else:
                    # Count wrapped lines
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) <= max_line_width:
                            current_line = test_line
                        else:
                            if current_line:
                                ts_lines += 1
                            current_line = word
                    if current_line:
                        ts_lines += 1

            # Calculate dynamic height based on max lines needed
            max_lines = max(python_lines, ts_lines)
            calculated_height = 200 + (max_lines * 60) + 100  # header + lines (60px per line for font 48) + footer
            final_height = max(self.initial_height, calculated_height)

            # SECOND PASS: Create image with calculated dimensions and draw content
            img = Image.new('RGB', (final_width, final_height), self.bg_color)
            draw = ImageDraw.Draw(img)

            # Draw title at top
            title = f"Solution: LeetCode #{problem['id']}"
            draw.text((60, 30), title, font=header_font, fill=self.header_color)

            # Draw thick vertical border barrier in the middle
            draw.rectangle(
                [(middle_x - barrier_width//2, 80), (middle_x + barrier_width//2, final_height - 40)],
                fill=(60, 60, 60)  # Darker gray barrier
            )

            # Left side: Python (with more padding from center)
            python_label = "PYTHON"
            draw.text((80, 150), python_label, font=header_font, fill=self.header_color)

            python_y = 280

            for line in python_code.split('\n'):
                # Determine if line is a comment (starts with // or #)
                is_comment = line.strip().startswith('//') or line.strip().startswith('#')
                line_color = self.comment_color if is_comment else self.text_color

                # Wrap long lines instead of truncating
                if len(line) <= max_line_width:
                    draw.text((60, python_y), line, font=code_font, fill=line_color)
                    python_y += 60
                else:
                    # Split long line into multiple lines
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) <= max_line_width:
                            current_line = test_line
                        else:
                            if current_line:
                                draw.text((60, python_y), current_line, font=code_font, fill=line_color)
                                python_y += 60
                            current_line = word
                    if current_line:
                        draw.text((60, python_y), current_line, font=code_font, fill=line_color)
                        python_y += 60

            # Right side: TypeScript (with more padding from center)
            ts_label = "TYPESCRIPT"
            draw.text((middle_x + barrier_width//2 + 80, 150), ts_label, font=header_font, fill=self.header_color)

            ts_y = 280
            ts_start_x = middle_x + barrier_width//2 + 80  # Start after barrier

            for line in typescript_code.split('\n'):
                # Determine if line is a comment (starts with // or #)
                is_comment = line.strip().startswith('//') or line.strip().startswith('#')
                line_color = self.comment_color if is_comment else self.text_color

                # Wrap long lines instead of truncating
                if len(line) <= max_line_width:
                    draw.text((ts_start_x, ts_y), line, font=code_font, fill=line_color)
                    ts_y += 60
                else:
                    # Split long line into multiple lines
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) <= max_line_width:
                            current_line = test_line
                        else:
                            if current_line:
                                draw.text((ts_start_x, ts_y), current_line, font=code_font, fill=line_color)
                                ts_y += 60
                            current_line = word
                    if current_line:
                        draw.text((ts_start_x, ts_y), current_line, font=code_font, fill=line_color)
                        ts_y += 60

            # Save image
            filename = f"leetcode_{problem['id']}_solution.png"
            filepath = self.output_dir / filename
            img.save(filepath, 'PNG', quality=95)

            logger.info(f"Generated code solution image ({final_width}x{final_height}px): {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error generating code image: {str(e)}")
            return None


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    generator = LeetCodeCodeImageGenerator()

    test_problem = {'id': 1, 'title': 'Two Sum'}

    python_code = """def twoSum(nums, target):
    # Store seen numbers
    seen = {}

    for i, num in enumerate(nums):
        # Calculate complement
        complement = target - num

        # Check if we've seen it
        if complement in seen:
            return [seen[complement], i]

        # Remember this number
        seen[num] = i

    return []"""

    typescript_code = """function twoSum(
  nums: number[],
  target: number
): number[] {
  // Store seen numbers
  const seen = new Map<number, number>();

  for (let i = 0; i < nums.length; i++) {
    // Calculate complement
    const complement = target - nums[i];

    // Check if we've seen it
    if (seen.has(complement)) {
      return [seen.get(complement)!, i];
    }

    // Remember this number
    seen.set(nums[i], i);
  }

  return [];
}"""

    result = generator.generate_code_solution_image(test_problem, python_code, typescript_code)
    if result:
        print(f"Generated: {result}")
