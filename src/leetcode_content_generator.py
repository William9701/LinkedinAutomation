import google.generativeai as genai
from typing import Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class LeetCodeContentGenerator:
    """Generates beginner-friendly LeetCode solution content for LinkedIn"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_solution_post(self, problem: Dict, problem_details: Optional[Dict] = None) -> Optional[str]:
        """
        Generate a LinkedIn post with step-by-step solution explanation

        Args:
            problem: Basic problem info (id, title, slug, acceptance_rate)
            problem_details: Detailed problem info (description, hints, etc.) - optional

        Returns:
            LinkedIn post content as plain text
        """
        try:
            # Build the prompt
            prompt = f"""
Create a LinkedIn post explaining how to solve this LeetCode problem step-by-step for beginners.

PROBLEM:
#{problem['id']}: {problem['title']}
Acceptance Rate: {problem['acceptance_rate']:.1f}%

CRITICAL POST FORMAT REQUIREMENTS:

HEADER (First 2 lines):
🎯 LeetCode #{problem['id']}: {problem['title']}

[blank line, then start content]

CONTENT STRUCTURE - BEGINNER-FRIENDLY APPROACH:

1. THE PROBLEM IN SIMPLE WORDS (2-3 sentences)
   - Explain what we need to do using everyday language
   - Use a real-world analogy (shopping cart, organizing books, etc.)

2. EXAMPLE WALKTHROUGH (show with simple data)
   - Use small, easy numbers/examples
   - Walk through step-by-step what happens

3. THE APPROACH (break it down)
   - List 3-4 simple steps anyone can follow
   - Use bullet points with → or •
   - Each step should be ONE simple action

4. THE SOLUTION PATTERN
   - Show a simple code snippet with 4-space indentation
   - Use Python (most readable)
   - Add inline comments explaining each line
   - Keep it under 10 lines if possible

5. WHY THIS WORKS
   - Explain the "aha!" moment
   - Why is this approach clever/efficient?

6. WRAP UP
   - Time/Space complexity in simple terms
   - One encouraging sentence for beginners

CRITICAL FORMATTING RULES:
- NO Markdown (no **, __, ~~, ```)
- NO hashtags in content (added separately)
- Use simple 4-space indentation for code
- Use → or • for lists
- Keep total under 1000 characters MAX (STRICT LinkedIn limit!)
- Make it conversational and encouraging
- Use "you" and "we" - make it personal
- BE BRIEF - cut unnecessary words!

TONE:
- Friendly mentor explaining to a beginner
- Encouraging and positive
- Use phrases like "Here's the trick", "The key insight", "Think of it like..."
- Make them feel smart for understanding it

EXAMPLE STRUCTURE (KEEP IT SHORT - under 1000 chars!):
🎯 LeetCode #1: Two Sum

Finding two numbers that add up to a target? Think of it like finding matching puzzle pieces.

The trick: Use a dictionary to remember what we've seen.

The approach:
→ For each number, check if its "partner" exists (target - number)
→ If yes, found it!
→ If no, save and continue

    def twoSum(nums, target):
        seen = {{}}
        for i, num in enumerate(nums):
            if target - num in seen:
                return [seen[target - num], i]
            seen[num] = i

Why it works: One pass, instant lookups. O(n) time!

This pattern works for tons of problems. Keep practicing! 🎯

NOW CREATE THE POST:
Problem: #{problem['id']} - {problem['title']}
"""

            # Generate content
            response = self.model.generate_content(prompt)
            content = response.text.strip()

            # Clean up any markdown that might have slipped through
            content = self._clean_formatting(content)

            # Enforce LinkedIn character limit (3000 max, aim for 2800 with hashtags)
            if len(content) > 2800:
                logger.warning(f"Content too long ({len(content)} chars), truncating...")
                content = content[:2800].rsplit('\n', 1)[0]  # Cut at last newline before limit

            logger.info(f"Generated solution post for: {problem['title']} ({len(content)} chars)")
            return content

        except Exception as e:
            logger.error(f"Error generating solution post: {str(e)}")
            return None

    def _clean_formatting(self, content: str) -> str:
        """Remove any Markdown formatting for LinkedIn"""
        # Remove bold, italic, strikethrough
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        content = re.sub(r'_([^_]+)_', r'\1', content)
        content = re.sub(r'~~([^~]+)~~', r'\1', content)

        # Remove headers
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

        # Remove code block markers (keep the code itself)
        content = re.sub(r'```\w*\n', '', content)
        content = re.sub(r'```', '', content)

        # Remove inline code markers (keep the text)
        content = re.sub(r'`([^`]+)`', r'\1', content)

        return content

    def generate_hashtags(self, problem: Dict) -> list:
        """Generate relevant hashtags for the problem"""
        base_tags = ["LeetCode", "CodingInterview", "DSA", "Programming"]

        # Add difficulty-specific tags
        base_tags.extend(["Beginner", "LearnToCode", "100DaysOfCode"])

        # Common algorithm tags
        common_tags = ["Algorithms", "ProblemSolving", "TechInterview", "SoftwareEngineering"]

        return base_tags + common_tags[:3]  # Limit to ~7 hashtags
