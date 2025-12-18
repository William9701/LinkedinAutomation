import logging
import os
import time
from pathlib import Path

from config import settings
from src.topic_manager import TopicManager
from src.content_generator import ContentGenerator
from src.image_generator import ImageGenerator
from src.linkedin_poster import LinkedInPoster
from src.scheduler import PostScheduler
from server import start_health_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class LinkedInAutomation:
    """Main automation orchestrator"""

    def __init__(self):
        self.topic_manager = TopicManager()
        self.content_generator = ContentGenerator(settings.gemini_api_key)
        self.image_generator = ImageGenerator(
            openai_api_key=settings.openai_api_key,
            replicate_token=settings.replicate_api_token
        )
        self.linkedin_poster = LinkedInPoster(settings.linkedin_access_token)
        self.scheduler = PostScheduler(timezone=settings.timezone)

    def create_and_post(self):
        """Main function to create and post content"""
        try:
            logger.info("Starting post creation process...")

            # Step 1: Get an unused topic
            topic = self.topic_manager.get_unused_topic()
            if not topic:
                logger.error("No topics available!")
                return False

            logger.info(f"Selected topic: {topic['title']}")

            # Step 2: Generate post content with Gemini
            logger.info("Generating post content with Gemini AI...")
            post_content = self.content_generator.generate_post_content(topic)
            if not post_content:
                logger.error("Failed to generate post content")
                return False

            logger.info(f"Generated content ({len(post_content)} chars)")

            # Step 3: Generate optimized hashtags
            logger.info("Generating optimized hashtags...")
            hashtags = self.content_generator.optimize_hashtags(topic, post_content)
            logger.info(f"Generated {len(hashtags)} hashtags: {', '.join(hashtags)}")

            # Step 4: Generate image (optional)
            image_path = None
            logger.info("Generating image prompt...")
            image_prompt = self.content_generator.generate_image_prompt(topic, post_content)

            if image_prompt:
                logger.info("Generating image...")
                image_path = self.image_generator.generate_image(
                    image_prompt,
                    filename=f"topic_{topic['id']}"
                )
                if image_path:
                    logger.info(f"Image generated: {image_path}")
                else:
                    logger.warning("Image generation failed, posting without image")

            # Step 5: Post to LinkedIn
            logger.info("Posting to LinkedIn...")
            if image_path and Path(image_path).exists():
                post_urn = self.linkedin_poster.create_image_post(
                    content=post_content,
                    image_path=image_path,
                    hashtags=hashtags
                )
            else:
                post_urn = self.linkedin_poster.create_text_post(
                    content=post_content,
                    hashtags=hashtags
                )

            if post_urn:
                logger.info(f"Successfully posted! URN: {post_urn}")
                # Mark topic as used
                self.topic_manager.mark_topic_used(topic['id'])
                return True
            else:
                logger.error("Failed to post to LinkedIn")
                return False

        except Exception as e:
            logger.error(f"Error in create_and_post: {str(e)}", exc_info=True)
            return False

    def run_scheduled(self, skip_startup_post=False):
        """Run the automation on a schedule"""
        logger.info("Starting LinkedIn Automation with scheduler...")

        # Start health check server for Render
        port = int(os.environ.get('PORT', 10000))
        start_health_server(port)

        # Post immediately on startup to verify system is working
        if not skip_startup_post:
            logger.info("=" * 60)
            logger.info("STARTUP TEST POST - Posting immediately to verify system works...")
            logger.info("=" * 60)
            success = self.create_and_post()
            if success:
                logger.info("✅ Startup test post successful! System is working correctly.")
            else:
                logger.error("❌ Startup test post failed! Check the logs above for errors.")
            logger.info("=" * 60)
            # Wait a bit before starting scheduler
            time.sleep(5)

        # Schedule daily posts
        self.scheduler.schedule_daily_posts(
            post_callback=self.create_and_post,
            morning_time=settings.morning_post_time,
            evening_time=settings.evening_post_time
        )

        # Start scheduler
        self.scheduler.start()

        # Print next scheduled times
        logger.info("Scheduled posts:")
        for job_info in self.scheduler.get_next_run_times():
            logger.info(f"  {job_info['name']}: {job_info['next_run']}")

        # Keep the program running
        try:
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler...")
            self.scheduler.stop()

    def run_once(self):
        """Run once immediately (for testing)"""
        logger.info("Running automation once (test mode)...")
        success = self.create_and_post()
        if success:
            logger.info("Test post completed successfully!")
        else:
            logger.error("Test post failed!")
        return success


def main():
    """Main entry point"""
    import sys

    automation = LinkedInAutomation()

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Run once for testing
            automation.run_once()
        elif sys.argv[1] == "schedule":
            # Run on schedule
            automation.run_scheduled()
        else:
            print("Usage: python main.py [test|schedule]")
            print("  test     - Run once immediately")
            print("  schedule - Run on configured schedule")
    else:
        # Default: run on schedule
        automation.run_scheduled()


if __name__ == "__main__":
    main()
