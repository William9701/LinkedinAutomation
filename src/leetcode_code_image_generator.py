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

        # Card dimensions
        self.width = 1200
        self.height = 800  # Taller for code

        # Colors
        self.bg_color = (30, 30, 30)  # Dark background for code
        self.text_color = (230, 230, 230)  # Light text
        self.comment_color = (106, 153, 85)  # Green for comments
        self.keyword_color = (86, 156, 214)  # Blue for keywords
        self.string_color = (206, 145, 120)  # Orange for strings
        self.divider_color = (100, 100, 100)  # Gray divider
        self.header_color = (255, 198, 0)  # Yellow for headers

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
            # Create image
            img = Image.new('RGB', (self.width, self.height), self.bg_color)
            draw = ImageDraw.Draw(img)

            # Fonts
            header_font = self._get_font(24, bold=True)
            code_font = self._get_font(16)

            # Draw title at top
            title = f"Solution: LeetCode #{problem['id']}"
            draw.text((60, 30), title, font=header_font, fill=self.header_color)

            # Draw vertical divider line in the middle
            middle_x = self.width // 2
            draw.line([(middle_x, 80), (middle_x, self.height - 40)], fill=self.divider_color, width=2)

            # Left side: Python
            python_label = "PYTHON"
            draw.text((80, 80), python_label, font=header_font, fill=self.header_color)

            python_y = 120
            for line in python_code.split('\n'):
                if python_y > self.height - 60:
                    break
                draw.text((60, python_y), line, font=code_font, fill=self.text_color)
                python_y += 22

            # Right side: TypeScript
            ts_label = "TYPESCRIPT"
            draw.text((middle_x + 80, 80), ts_label, font=header_font, fill=self.header_color)

            ts_y = 120
            for line in typescript_code.split('\n'):
                if ts_y > self.height - 60:
                    break
                draw.text((middle_x + 60, ts_y), line, font=code_font, fill=self.text_color)
                ts_y += 22

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
