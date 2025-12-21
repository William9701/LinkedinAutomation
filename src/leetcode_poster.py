"""
Complete workflow for posting LeetCode problems
"""
import logging
from typing import Optional, Dict
from .leetcode_fetcher import LeetCodeFetcher
from .leetcode_image_generator import LeetCodeImageGenerator
from .leetcode_code_image_generator import LeetCodeCodeImageGenerator
from .leetcode_solution_generator import LeetCodeSolutionGenerator
from .linkedin_poster import LinkedInPoster
from .topic_manager import TopicManager
from .combine_images import combine_images_vertical

logger = logging.getLogger(__name__)


class LeetCodePoster:
    """Handles the complete LeetCode posting workflow"""

    def __init__(
        self,
        gemini_api_key: str,
        linkedin_access_token: str
    ):
        self.fetcher = LeetCodeFetcher()
        self.question_image_generator = LeetCodeImageGenerator()
        self.code_image_generator = LeetCodeCodeImageGenerator()
        self.solution_generator = LeetCodeSolutionGenerator(gemini_api_key)
        self.linkedin_poster = LinkedInPoster(linkedin_access_token)
        self.topic_manager = TopicManager()

    def post_leetcode_problem(self, topic: Optional[Dict] = None) -> Optional[str]:
        """
        Complete workflow: Get problem, generate image + solution, post with comment

        Args:
            topic: Topic dict with LeetCode problem info (optional, will get random if None)

        Returns:
            Post URN if successful
        """
        try:
            # Get a LeetCode topic
            if not topic:
                topic = self.topic_manager.get_unused_topic()
                if not topic or not topic.get('category', '').startswith('LeetCode'):
                    logger.error("No LeetCode topic available")
                    return None

            logger.info(f"Processing LeetCode problem: {topic['title']}")

            # Extract problem info from topic
            problem = {
                'id': topic.get('leetcode_id'),
                'title': topic['title'].replace(f"LeetCode #{topic.get('leetcode_id')}: ", ""),
                'slug': topic.get('leetcode_slug'),
                'acceptance_rate': topic.get('acceptance_rate', 0)
            }

            # Step 1: Get detailed problem info from LeetCode API
            logger.info("Fetching problem details...")
            problem_details = None
            if problem['slug']:
                problem_details = self.fetcher.get_problem_details(problem['slug'])

            # Step 2: Generate QUESTION image (Image 1)
            logger.info("Generating question image...")
            question_image_path = self.question_image_generator.generate_problem_image(problem, problem_details)

            if not question_image_path:
                logger.error("Failed to generate question image")
                return None

            # Step 3: Generate COMPLETE SOLUTION (Python + TypeScript + Explanation)
            logger.info("Generating complete solution...")
            solution = self.solution_generator.generate_complete_solution(problem, problem_details)

            if not solution:
                logger.error("Failed to generate solution")
                return None

            # Step 4: Generate CODE image (Image 2: Python | TypeScript side-by-side)
            logger.info("Generating code solution image...")
            code_image_path = self.code_image_generator.generate_code_solution_image(
                problem,
                solution['python_code'],
                solution['typescript_code']
            )

            if not code_image_path:
                logger.error("Failed to generate code image")
                return None

            # Step 5: Combine both images (question on top, code on bottom)
            logger.info("Combining question and code images...")
            combined_image_path = combine_images_vertical(question_image_path, code_image_path)

            if not combined_image_path:
                logger.error("Failed to combine images")
                return None

            # Step 6: Prepare post content with problem title and explanation
            problem_title = f"LeetCode #{problem['id']}: {problem['title']}\n\n"
            post_content = problem_title + solution['explanation']

            # Step 7: Standard hashtags for all posts
            hashtags = [
                'Algorithms', 'Coding', 'Python', 'SoftwareEngineering',
                'ProblemSolving', 'CodeChallenges', 'Technology', 'Learning',
                'Innovation', 'LogicPuzzles', 'CriticalThinking', 'BrainTeaser',
                'CareerGrowth', 'TechTips', 'PersonalDevelopment'
            ]

            # Step 8: Post to LinkedIn with COMBINED image
            # Combined Image = Question + Code, Post = Explanation
            logger.info("Posting to LinkedIn with combined image...")
            post_urn = self.linkedin_poster.create_image_post(
                content=post_content,  # THE EXPLANATION
                image_path=combined_image_path,  # COMBINED IMAGE (question + code)
                hashtags=hashtags
            )
            if post_urn:
                # Mark topic as used
                self.topic_manager.mark_topic_used(topic['id'])
                logger.info(f"Successfully posted LeetCode problem: {post_urn}")
                return post_urn
            else:
                logger.error("Failed to post to LinkedIn")
                return None

        except Exception as e:
            logger.error(f"Error in LeetCode posting workflow: {str(e)}")
            return None


if __name__ == "__main__":
    # Test the workflow
    import os
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    gemini_key = os.getenv('GEMINI_API_KEY')
    linkedin_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

    if gemini_key and linkedin_token:
        poster = LeetCodePoster(gemini_key, linkedin_token)
        result = poster.post_leetcode_problem()
        if result:
            print(f"Success! Post URN: {result}")
        else:
            print("Failed to post")
    else:
        print("Missing API keys in .env file")
