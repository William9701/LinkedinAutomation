import google.generativeai as genai
from typing import Dict, Optional
import logging
from .special_days import SpecialDayDetector

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates content using Google Gemini AI"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Using gemini-2.5-flash - free tier available
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.special_day_detector = SpecialDayDetector()

    def generate_post_content(self, topic: Dict) -> Optional[str]:
        """
        Generate LinkedIn post content from a topic

        Args:
            topic: Topic dictionary with 'title', 'category', and 'prompt'

        Returns:
            Generated post content as string
        """
        try:
            enhanced_prompt = f"""
{topic['prompt']}

CRITICAL FORMATTING REQUIREMENTS FOR LINKEDIN:

HEADER FORMAT (FIRST 2 LINES - VERY IMPORTANT):
- Line 1: Start with 1-2 relevant emojis, then the topic title in a compelling way
- Line 2: Leave blank
- Line 3: Start the actual content with a hook

Example header format:
💡 Why Your App Might Be Slower Than It Should Be

Last week, I discovered something that changed how I build APIs...

CONTENT REQUIREMENTS - ACCESSIBLE & ENGAGING:
1. Write in first person, but as someone sharing a discovery or story ("I recently learned", "Here's what surprised me")
2. Start with a HOOK - something relatable, surprising, or curious
3. Use ANALOGIES and REAL-WORLD COMPARISONS - tech concepts explained through everyday things
4. Use short paragraphs (2-3 sentences max) for easy mobile reading
5. Make it conversational - like explaining to a smart friend at a coffee shop
6. Include specific examples, but explain WHY they matter in simple terms
7. Keep under 1300 characters for optimal LinkedIn algorithm performance
8. End with a thought-provoking question that ANYONE can answer (not just devs)

STORYTELLING STRUCTURE:
1. Hook (relatable opening or surprising fact)
2. The Discovery (what you learned/observed)
3. Why It Matters (practical impact in simple terms)
4. Call to Action (engaging question)

LANGUAGE STYLE:
- Avoid heavy jargon - explain technical terms simply
- Use "you" and "your" to make it personal
- Paint pictures with words - make concepts visual
- Add human emotion and experience
- Make non-technical people feel welcome

LINKEDIN FORMATTING RULES - CRITICAL:
- DO NOT use Markdown (no **, __, ~~, etc.) - LinkedIn shows these as literal characters
- DO NOT use headers with # symbols
- DO NOT use code blocks with backticks (```)
- For code snippets: Use simple indentation (4 spaces) with plain text
- Use line breaks and spacing instead of formatting
- Use → or • for bullet points if needed
- Keep it clean, professional, plain text
- DO NOT include hashtags in the content (they will be added separately)
- If code is complex, reference it briefly and let the image show the details

EMOJI GUIDELINES FOR HEADER:
- Choose 1-2 emojis that relate to the feeling/benefit, not just the tech
- Discovery/Learning: 💡 ✨ 🎯 🔍 💭
- Problem-Solving: 🤔 ⚡ 🔧 🛠️
- Performance/Speed: 🚀 ⚡ 📈 💨
- Security/Safety: 🔒 🛡️ 🔐 🎯
- Simplicity/Clarity: ✨ 💡 🎨 🧩
- Innovation: 🚀 🤖 🧠 ✨ 🎯

TONE: Friendly, curious, and accessible. Like a knowledgeable friend sharing something cool they discovered. NOT resume-speak or LinkedIn-corporate.

Category: {topic['category']}
Topic: {topic['title']}

EXAMPLE (Accessible Style):
💡 THE CHECKOUT LANE PRINCIPLE

Think about the last time you were at a grocery store. Express lane vs regular lane - same groceries, different wait times.

That's exactly how choosing between different API frameworks works. Some are built like express lanes (FastAPI) - they handle one thing at a time super fast. Others are like regular lanes (traditional frameworks) - they wait for each task to finish before starting the next.

The difference? In a busy app, it's like having 100 people in line. Express lanes keep things moving.

The surprising part: Most apps don't need express lanes at all. It's about matching the tool to your actual traffic.

What's your go-to approach - speed optimization or simplicity first?
"""

            # Add special day context if applicable
            special_day_enhancement = self.special_day_detector.get_prompt_enhancement()
            if special_day_enhancement:
                enhanced_prompt += special_day_enhancement

            enhanced_prompt += "\n\nGenerate the LinkedIn post now with the eye-catching header format:"

            response = self.model.generate_content(enhanced_prompt)

            if response and response.text:
                # Clean up the content to remove any Markdown formatting
                cleaned_content = self._clean_linkedin_formatting(response.text.strip())

                # Add special day context as a closing if not already naturally included
                special_day_context = self.special_day_detector.get_post_context()
                if special_day_context:
                    # Only add if the AI didn't already mention the special day
                    special_day_info = self.special_day_detector.get_special_day_info()
                    if special_day_info:
                        day_name = special_day_info.get("name", "")
                        # Check if day is already mentioned in content
                        if day_name.lower() not in cleaned_content.lower():
                            cleaned_content += special_day_context

                return cleaned_content
            else:
                logger.error("Empty response from Gemini")
                return None

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return None

    def generate_image_prompt(self, topic: Dict, post_content: str) -> Optional[str]:
        """
        Generate an image description prompt for the post

        Args:
            topic: Topic dictionary
            post_content: Generated post content

        Returns:
            Image generation prompt
        """
        try:
            prompt = f"""
Based on this LinkedIn post about {topic['title']}, create a detailed image generation prompt for a professional, visually appealing illustration.

Post content:
{post_content[:500]}...

Generate a prompt for creating a clean, modern, professional image that:
1. Represents the technical concept visually
2. Uses a tech/corporate color scheme (blues, greens, grays)
3. Is minimalist and professional (no stock photo people)
4. Could include: diagrams, architecture illustrations, code snippets, or abstract tech concepts
5. Is suitable for LinkedIn's professional audience

Return ONLY the image generation prompt, nothing else.
"""

            response = self.model.generate_content(prompt)

            if response and response.text:
                return response.text.strip()
            else:
                logger.error("Empty response from Gemini for image prompt")
                return None

        except Exception as e:
            logger.error(f"Error generating image prompt: {str(e)}")
            return None

    def optimize_hashtags(self, topic: Dict, post_content: str) -> list[str]:
        """
        Generate optimized hashtags for the post

        Args:
            topic: Topic dictionary
            post_content: Generated post content

        Returns:
            List of hashtags (without # symbol)
        """
        try:
            prompt = f"""
Based on this LinkedIn post, generate 10-15 optimal hashtags for maximum reach and engagement.

Category: {topic['category']}
Title: {topic['title']}
Content: {post_content[:300]}...

Requirements:
1. Mix of popular (100K+ posts) and niche (10K-100K posts) hashtags
2. Include both TECHNICAL tags (for developers) AND GENERAL tags (for broader audience)
3. Technical tags: Python, BackendDevelopment, SoftwareEngineering, specific technologies
4. General tags: Productivity, Learning, Innovation, CareerGrowth, Technology, TechTips
5. Make it accessible - non-developers should feel welcome
6. Include trending topics when relevant

Return ONLY a comma-separated list of hashtags WITHOUT the # symbol.
Example format: Technology, Innovation, Python, BackendDevelopment, Learning, Productivity, SoftwareEngineering
"""

            response = self.model.generate_content(prompt)

            if response and response.text:
                # Parse hashtags from response
                hashtags_text = response.text.strip()
                # Remove any # symbols if present
                hashtags_text = hashtags_text.replace('#', '')
                # Split by comma and clean
                hashtags = [tag.strip() for tag in hashtags_text.split(',')]
                # Remove empty strings and limit to 15
                hashtags = [tag for tag in hashtags if tag][:15]
                return hashtags
            else:
                # Fallback hashtags
                return self._get_fallback_hashtags(topic)

        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return self._get_fallback_hashtags(topic)

    def _get_fallback_hashtags(self, topic: Dict) -> list[str]:
        """Fallback hashtags based on category"""
        base_tags = [
            "Technology",
            "Innovation",
            "Learning",
            "SoftwareEngineering",
            "BackendDevelopment",
            "Python",
            "Productivity",
            "TechTips",
            "CareerGrowth",
            "SoftwareDevelopment"
        ]

        category_tags = {
            "Architecture & Design": ["SoftwareArchitecture", "SystemDesign", "APIDesign"],
            "AI & Development": ["ArtificialIntelligence", "MachineLearning", "AIEngineering"],
            "Database Strategy": ["Database", "PostgreSQL", "MongoDB", "DataEngineering"],
            "System Design": ["SystemDesign", "DistributedSystems", "Scalability"],
            "DevOps & Infrastructure": ["DevOps", "Kubernetes", "CloudComputing", "Docker"],
            "API Design": ["API", "RESTful", "GraphQL", "Microservices"],
            "Testing Strategy": ["Testing", "QualityAssurance", "DevOps"],
            "AI Engineering": ["LLM", "GPT", "RAG", "AIEngineering"],
            "Backend Patterns": ["Microservices", "Architecture", "DesignPatterns"],
            "Performance": ["Performance", "Optimization", "Database"],
            "Security": ["CyberSecurity", "AppSec", "OAuth", "Security"],
            "Career Development": ["CareerGrowth", "TechCareer", "Leadership"],
            "Observability": ["Observability", "Monitoring", "SRE", "DevOps"],
            "AI/ML Operations": ["MLOps", "LLM", "MachineLearning"],
            "CI/CD": ["CICD", "DevOps", "Automation", "GitLab"]
        }

        category = topic.get("category", "")
        specific_tags = category_tags.get(category, [])

        return base_tags + specific_tags

    def _clean_linkedin_formatting(self, content: str) -> str:
        """
        Remove Markdown formatting that doesn't work on LinkedIn
        LinkedIn uses plain text, so we need to strip all Markdown syntax
        """
        import re

        # Remove bold (**text** or __text__)
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
        content = re.sub(r'__(.+?)__', r'\1', content)

        # Remove italic (*text* or _text_)
        content = re.sub(r'\*(.+?)\*', r'\1', content)
        content = re.sub(r'_(.+?)_', r'\1', content)

        # Remove strikethrough (~~text~~)
        content = re.sub(r'~~(.+?)~~', r'\1', content)

        # Remove code blocks (```text```)
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        # Remove inline code (`text`)
        content = re.sub(r'`(.+?)`', r'\1', content)

        # Remove headers (# Header)
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)

        # Remove horizontal rules (--- or ***)
        content = re.sub(r'^(\*{3,}|-{3,})$', '', content, flags=re.MULTILINE)

        # Remove mentions of specific years of experience
        content = re.sub(r'(?i)(after|with|my|over)\s*\d+\s*years?\s+(in|of|as|managing|building|working)\s+', r'\1 extensive experience \2 ', content)
        content = re.sub(r'(?i)\d+\s*years?\s+(in|of)\s+', r'extensive experience \1 ', content)
        content = re.sub(r'(?i)\d+-year\s+(veteran|experience)', r'experienced', content)
        content = re.sub(r'(?i)after\s+\d+\s+years', 'in my experience', content)

        # Clean up multiple consecutive blank lines (keep max 2)
        content = re.sub(r'\n{4,}', '\n\n\n', content)

        return content.strip()
