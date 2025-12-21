"""
Test LeetCode content generation WITHOUT posting to LinkedIn
"""
import os
import sys
import logging
from dotenv import load_dotenv

sys.path.insert(0, '.')

from src.leetcode_fetcher import LeetCodeFetcher
from src.leetcode_image_generator import LeetCodeImageGenerator
from src.leetcode_code_image_generator import LeetCodeCodeImageGenerator
from src.leetcode_solution_generator import LeetCodeSolutionGenerator
from src.combine_images import combine_images_vertical
from src.topic_manager import TopicManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def test_generation():
    """Generate complete LeetCode post WITHOUT posting"""

    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env")
        return

    # Initialize components
    topic_manager = TopicManager()
    fetcher = LeetCodeFetcher()
    question_image_gen = LeetCodeImageGenerator()
    code_image_gen = LeetCodeCodeImageGenerator()
    solution_gen = LeetCodeSolutionGenerator(api_key)

    # Get a random LeetCode topic
    topic = topic_manager.get_unused_topic()
    if not topic or not topic.get('category', '').startswith('LeetCode'):
        print("ERROR: No LeetCode topic available")
        return

    logger.info(f"Selected: {topic['title']}")

    # Extract problem info
    problem = {
        'id': topic.get('leetcode_id'),
        'title': topic['title'].replace(f"LeetCode #{topic.get('leetcode_id')}: ", ""),
        'slug': topic.get('leetcode_slug'),
        'acceptance_rate': topic.get('acceptance_rate', 0)
    }

    # Get problem details
    logger.info("Fetching problem details from LeetCode...")
    problem_details = None
    if problem['slug']:
        problem_details = fetcher.get_problem_details(problem['slug'])

    # Generate question image
    logger.info("Generating question image...")
    question_img = question_image_gen.generate_problem_image(problem, problem_details)
    print(f"\n✓ Question image: {question_img}")

    # Generate complete solution
    logger.info("Generating solution (Python + TypeScript + Explanation)...")
    solution = solution_gen.generate_complete_solution(problem, problem_details)

    if not solution:
        print("ERROR: Failed to generate solution")
        return

    # Save solution to file
    solution_file = f"test_solution_leetcode_{problem['id']}.txt"
    with open(solution_file, 'w', encoding='utf-8') as f:
        f.write(f"=== LEETCODE #{problem['id']}: {problem['title']} ===\n\n")
        f.write("=== PYTHON CODE ===\n")
        f.write(solution['python_code'])
        f.write("\n\n=== TYPESCRIPT CODE ===\n")
        f.write(solution['typescript_code'])
        f.write("\n\n=== LINKEDIN POST (EXPLANATION) ===\n")
        f.write(solution['explanation'])

    print(f"✓ Solution saved: {solution_file}")

    # Generate code image
    logger.info("Generating code image...")
    code_img = code_image_gen.generate_code_solution_image(
        problem,
        solution['python_code'],
        solution['typescript_code']
    )
    print(f"✓ Code image: {code_img}")

    # Combine images
    logger.info("Combining images...")
    combined_img = combine_images_vertical(question_img, code_img)
    print(f"✓ Combined image: {combined_img}")

    print("\n" + "="*80)
    print("SUCCESS! Generated complete LeetCode post content:")
    print("="*80)
    print(f"📸 Combined Image: {combined_img}")
    print(f"📝 Explanation Text: {solution_file}")
    print(f"🏷️  Hashtags: #LeetCode #CodingInterview #DSA #Programming #Python #TypeScript")
    print("\n" + "="*80)
    print("READY TO POST!")
    print("="*80)


if __name__ == "__main__":
    test_generation()
