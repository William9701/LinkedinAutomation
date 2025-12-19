"""
Complete workflow for posting LeetCode problems
"""
import logging
from typing import Optional, Dict
from .leetcode_fetcher import LeetCodeFetcher
from .leetcode_image_generator import LeetCodeImageGenerator
from .leetcode_content_generator import LeetCodeContentGenerator
from .linkedin_poster import LinkedInPoster
from .topic_manager import TopicManager

logger = logging.getLogger(__name__)


class LeetCodePoster:
    """Handles the complete LeetCode posting workflow"""

    def __init__(
        self,
        gemini_api_key: str,
        linkedin_access_token: str
    ):
        self.fetcher = LeetCodeFetcher()
        self.image_generator = LeetCodeImageGenerator()
        self.content_generator = LeetCodeContentGenerator(gemini_api_key)
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
                if not topic or topic.get('category') != 'LeetCode Easy':
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

            # Step 1: Generate the problem image
            logger.info("Generating problem image...")
            # Try to get detailed problem info
            problem_details = None
            if problem['slug']:
                problem_details = self.fetcher.get_problem_details(problem['slug'])

            image_path = self.image_generator.generate_problem_image(problem, problem_details)

            if not image_path:
                logger.error("Failed to generate image")
                return None

            # Step 2: Generate the solution content
            logger.info("Generating solution content...")
            solution_content = self.content_generator.generate_solution_post(problem, problem_details)

            if not solution_content:
                logger.error("Failed to generate solution")
                return None

            # Step 3: Create main post content (short hook to engage)
            main_post_content = f"""🎯 LeetCode #{problem['id']}: {problem['title']}

Can you solve this coding challenge?

Think about your approach, then check the comments for my step-by-step solution! 👇"""

            # Step 4: Generate hashtags
            hashtags = self.content_generator.generate_hashtags(problem)

            # Step 5: Post to LinkedIn with image and solution as comment
            logger.info("Posting to LinkedIn...")
            post_urn = self.linkedin_poster.create_image_post_with_comment(
                main_content=main_post_content,
                comment_content=solution_content,
                image_path=image_path,
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
