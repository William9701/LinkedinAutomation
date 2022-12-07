"""
Test script to generate content for a single topic
This lets you see the output before posting to LinkedIn
"""

import json
import sys
from src.topic_manager import TopicManager
from src.content_generator import ContentGenerator


def test_content_generation(gemini_api_key=None):
    """Test content generation with a topic"""

    # Load first topic
    topic_manager = TopicManager()
    topics = topic_manager.get_all_topics()

    if not topics:
        print("No topics found!")
        return

    # Get first topic
    topic = topics[0]

    print("=" * 80)
    print("TOPIC SELECTED")
    print("=" * 80)
    print(f"ID: {topic['id']}")
    print(f"Category: {topic['category']}")
    print(f"Title: {topic['title']}")
    print(f"\nPrompt for AI:")
    print(topic['prompt'])
    print("=" * 80)

    # If API key provided, generate content
    if gemini_api_key:
        print("\nGenerating content with Gemini AI...")
        print("-" * 80)

        try:
            content_generator = ContentGenerator(gemini_api_key)

            # Generate post content
            post_content = content_generator.generate_post_content(topic)

            if post_content:
                print("\nGENERATED POST CONTENT:")
                print("=" * 80)
                print(post_content)
                print("=" * 80)
                print(f"\nContent length: {len(post_content)} characters")

                # Generate hashtags
                print("\nGenerating hashtags...")
                hashtags = content_generator.optimize_hashtags(topic, post_content)
                print(f"\nGENERATED HASHTAGS ({len(hashtags)}):")
                print(" ".join([f"#{tag}" for tag in hashtags]))

                # Generate image prompt
                print("\nGenerating image prompt...")
                image_prompt = content_generator.generate_image_prompt(topic, post_content)
                if image_prompt:
                    print("\nIMAGE GENERATION PROMPT:")
                    print("-" * 80)
                    print(image_prompt)
                    print("-" * 80)

                # Show final post preview
                print("\n" + "=" * 80)
                print("FINAL POST PREVIEW")
                print("=" * 80)
                print(post_content)
                print()
                print(" ".join([f"#{tag}" for tag in hashtags]))
                print("=" * 80)

            else:
                print("Failed to generate content!")

        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("\nTo generate content, provide your Gemini API key:")
        print("python test_content_generation.py YOUR_GEMINI_API_KEY")
        print("\nOr set it in your .env file and run:")
        print("python -c \"from dotenv import load_dotenv; load_dotenv(); import os; exec(open('test_content_generation.py').read())\"")


if __name__ == "__main__":
    # Check if API key provided as argument
    api_key = sys.argv[1] if len(sys.argv) > 1 else None

    # Or try to load from .env
    if not api_key:
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
        except:
            pass

    test_content_generation(api_key)
