"""
Test script to generate LeetCode images without posting
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.leetcode_fetcher import LeetCodeFetcher
from src.leetcode_image_generator import LeetCodeImageGenerator
from src.leetcode_solution_generator import LeetCodeSolutionGenerator
from src.leetcode_code_image_generator import LeetCodeCodeImageGenerator
from src.combine_images import combine_images_vertical
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_image_generation():
    """Test generating images for a LeetCode problem"""

    # Initialize components
    fetcher = LeetCodeFetcher()
    image_gen = LeetCodeImageGenerator()
    solution_gen = LeetCodeSolutionGenerator(api_key=os.getenv("GEMINI_API_KEY"))
    code_image_gen = LeetCodeCodeImageGenerator()

    # Test with problem #3206 (the one in the screenshot)
    problem_slug = "alternating-groups-i"
    problem_id = 3206

    logger.info(f"Testing with LeetCode problem: {problem_slug}")

    # Step 1: Fetch problem details
    logger.info("Fetching problem details...")
    problem_details = fetcher.get_problem_details(problem_slug)
    if not problem_details:
        logger.error(f"Could not fetch details for problem: {problem_slug}")
        return

    # Create problem dict for image generators
    problem = {
        'id': problem_id,
        'title': problem_details.get('title', 'Unknown'),
        'slug': problem_slug
    }

    logger.info(f"Problem: {problem['title']}")
    logger.info(f"Difficulty: {problem_details.get('difficulty', 'Unknown')}")

    # Step 2: Generate question image
    logger.info("Generating question image...")
    question_image_path = image_gen.generate_problem_image(problem, problem_details)
    if not question_image_path:
        logger.error("Failed to generate question image")
        return
    logger.info(f"Question image saved to: {question_image_path}")

    # Step 3: Generate solutions
    logger.info("Generating solutions with Gemini AI...")
    result = solution_gen.generate_complete_solution(problem, problem_details)
    if not result:
        logger.error("Failed to generate solutions")
        return

    python_code = result['python_code']
    typescript_code = result['typescript_code']
    explanation = result['explanation']

    logger.info(f"Explanation length: {len(explanation)} characters")

    # Step 4: Generate code solution image
    logger.info("Generating code solution image...")
    code_image_path = code_image_gen.generate_code_solution_image(
        problem,
        python_code,
        typescript_code
    )
    if not code_image_path:
        logger.error("Failed to generate code image")
        return
    logger.info(f"Code image saved to: {code_image_path}")

    # Step 5: Combine images
    logger.info("Combining question and code images...")
    combined_image_path = combine_images_vertical(question_image_path, code_image_path)
    logger.info(f"Combined image saved to: {combined_image_path}")

    logger.info("\n" + "="*60)
    logger.info("✅ IMAGE GENERATION COMPLETE!")
    logger.info("="*60)
    logger.info(f"Question Image: {question_image_path}")
    logger.info(f"Code Image: {code_image_path}")
    logger.info(f"Combined Image: {combined_image_path}")
    logger.info(f"\nExplanation Preview (first 500 chars):")
    logger.info(explanation[:500] + "...")
    logger.info("="*60)

if __name__ == "__main__":
    test_image_generation()
