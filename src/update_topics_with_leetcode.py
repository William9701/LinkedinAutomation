"""
Script to add LeetCode problems to the topics library
Run this to populate your topics with algorithm content
"""
import json
import logging
from src.leetcode_fetcher import LeetCodeFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_leetcode_to_topics(
    easy_count: int = 100,
    medium_count: int = 50,
    hard_count: int = 30,
    topics_file: str = "topics.json"
):
    """Add LeetCode problems of ALL difficulties to topics library"""

    # Fetch LeetCode problems (mixed difficulties)
    fetcher = LeetCodeFetcher()
    problems = fetcher.get_all_difficulties(easy_count, medium_count, hard_count)

    if not problems:
        logger.error("Failed to fetch LeetCode problems")
        return 0

    # Load existing topics
    try:
        with open(topics_file, 'r', encoding='utf-8') as f:
            topics_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Topics file not found: {topics_file}")
        return 0

    # Get current max ID
    existing_topics = topics_data.get('topics', [])
    max_id = max((topic['id'] for topic in existing_topics), default=0)

    # Add LeetCode problems as topics
    new_topics = []
    for i, problem in enumerate(problems):
        difficulty = problem.get('difficulty', 'Easy')
        topic = {
            "id": max_id + i + 1,
            "category": f"LeetCode {difficulty}",
            "title": f"LeetCode #{problem['id']}: {problem['title']}",
            "prompt": f"""Generate a beginner-friendly LinkedIn post solving LeetCode problem #{problem['id']}: {problem['title']}.

IMPORTANT: This is a coding problem explanation post. Follow the LeetCode solution format:

1. Explain the problem in simple words with a real-world analogy
2. Show a step-by-step example with small numbers
3. Break down the approach into 3-4 simple steps
4. Provide a clean Python code solution with comments (use 4-space indentation, NO code blocks)
5. Explain why this works and the time/space complexity simply
6. End with an encouraging note for beginners

Acceptance Rate: {problem['acceptance_rate']:.1f}%
Problem Slug: {problem['slug']}

Make it friendly, encouraging, and accessible to coding beginners!""",
            "used": False,
            "leetcode_id": problem['id'],
            "leetcode_slug": problem['slug'],
            "difficulty": difficulty,
            "difficulty_level": problem.get('difficulty_level', 1),
            "acceptance_rate": round(problem['acceptance_rate'], 1)
        }
        new_topics.append(topic)

    # Add to topics data
    topics_data['topics'].extend(new_topics)

    # Save back to file
    try:
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump(topics_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Added {len(new_topics)} LeetCode problems to topics")
        logger.info(f"Total topics now: {len(topics_data['topics'])}")
        return len(new_topics)
    except Exception as e:
        logger.error(f"Error saving topics: {str(e)}")
        return 0


if __name__ == "__main__":
    # Add LeetCode problems: 100 Easy, 50 Medium, 30 Hard = 180 total
    added = add_leetcode_to_topics(easy_count=100, medium_count=50, hard_count=30)
    print(f"\nSuccessfully added {added} LeetCode problems to topics library!")
    print("Mix: 100 Easy + 50 Medium + 30 Hard")
    print("These will now be rotated into your automated posting schedule.")
