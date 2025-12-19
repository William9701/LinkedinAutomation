"""
Generate complete LeetCode solutions: Python code, TypeScript code, and beginner explanation
"""
import google.generativeai as genai
from typing import Dict, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class LeetCodeSolutionGenerator:
    """Generates complete solutions with code in both languages and explanations"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_complete_solution(
        self,
        problem: Dict,
        problem_details: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Generate Python code, TypeScript code, and beginner explanation

        Returns:
            Dict with 'python_code', 'typescript_code', 'explanation'
        """
        try:
            prompt = f"""
Generate a COMPLETE solution for this LeetCode problem.

PROBLEM: #{problem['id']} - {problem['title']}

YOU MUST PROVIDE 3 THINGS:

1. PYTHON SOLUTION (with inline comments)
2. TYPESCRIPT SOLUTION (with inline comments matching Python)
3. BEGINNER-FRIENDLY EXPLANATION

=== PYTHON CODE REQUIREMENTS ===
- Clean, readable Python code
- Add inline comments explaining EACH step (// Step 1: Initialize...)
- Use descriptive variable names
- Keep it under 25 lines
- Format:
```python
def functionName(params):
    # Step 1: Describe what this does
    code here

    # Step 2: Next step
    more code
```

=== TYPESCRIPT CODE REQUIREMENTS ===
- Equivalent TypeScript solution
- SAME logic and comments as Python
- Use proper TypeScript types
- Format:
```typescript
function functionName(params: type[]): returnType {{
    // Step 1: Describe what this does (SAME as Python)
    code here

    // Step 2: Next step (SAME as Python)
    more code
}}
```

=== EXPLANATION REQUIREMENTS ===
Write a DETAILED explanation for beginners:

Structure:
1. THE PROBLEM IN SIMPLE WORDS (2-3 sentences with analogy)
   Example: "Think of this like organizing books on a shelf..."

2. LIVE WALKTHROUGH WITH EXAMPLE
   - Use simple example: [2, 7, 11, 15], target = 9
   - Walk through STEP BY STEP what the code does
   - Show what variables hold at each step
   - Example format:
     "Step 1: We create an empty dictionary 'seen' to remember numbers
      seen = {{}}

      Step 2: Look at first number: 2
      - We need 9, we have 2, so we need 7
      - Is 7 in our 'seen' dict? No
      - So we save: seen[2] = 0 (position)

      Step 3: Look at second number: 7..."

3. THE CODE BREAKDOWN
   - Reference specific line numbers from the code
   - Explain WHY each step matters
   - Connect to the comments in the code

4. WHY THIS WORKS
   - The "aha!" moment
   - Time/Space complexity in simple terms

5. TIPS FOR BEGINNERS
   - Common mistakes to avoid
   - How to recognize this pattern in other problems

CRITICAL RULES:
- NO markdown formatting (no **, __, ```)
- Make it CONVERSATIONAL and ENCOURAGING
- Use "you", "we", "let's"
- REFERENCE the comments in your code (e.g., "In Step 1 of the code...")
- Keep explanation under 2000 characters
- Be SPECIFIC with examples

OUTPUT FORMAT:
=== PYTHON ===
[python code here]

=== TYPESCRIPT ===
[typescript code here]

=== EXPLANATION ===
[detailed explanation here]

NOW GENERATE THE COMPLETE SOLUTION FOR:
Problem #{problem['id']}: {problem['title']}
"""

            if problem_details and problem_details.get('content'):
                # Add problem description
                content = problem_details['content']
                content = re.sub(r'<[^>]+>', ' ', content)
                content = re.sub(r'\s+', ' ', content).strip()[:500]
                prompt += f"\n\nProblem Description:\n{content}"

            # Generate
            response = self.model.generate_content(prompt)
            content = response.text.strip()

            # Parse the response
            python_match = re.search(r'=== PYTHON ===\s*\n(.*?)\n=== TYPESCRIPT ===', content, re.DOTALL)
            typescript_match = re.search(r'=== TYPESCRIPT ===\s*\n(.*?)\n=== EXPLANATION ===', content, re.DOTALL)
            explanation_match = re.search(r'=== EXPLANATION ===\s*\n(.*)', content, re.DOTALL)

            if not (python_match and typescript_match and explanation_match):
                logger.error("Failed to parse generated solution")
                return None

            python_code = python_match.group(1).strip()
            typescript_code = typescript_match.group(1).strip()
            explanation = explanation_match.group(1).strip()

            # Clean up code blocks
            python_code = re.sub(r'```python\n?', '', python_code)
            python_code = re.sub(r'```\n?', '', python_code)
            typescript_code = re.sub(r'```typescript\n?', '', typescript_code)
            typescript_code = re.sub(r'```\n?', '', typescript_code)

            # Clean explanation
            explanation = self._clean_formatting(explanation)

            logger.info(f"Generated complete solution for: {problem['title']}")
            return {
                'python_code': python_code.strip(),
                'typescript_code': typescript_code.strip(),
                'explanation': explanation.strip()
            }

        except Exception as e:
            logger.error(f"Error generating solution: {str(e)}")
            return None

    def _clean_formatting(self, content: str) -> str:
        """Remove markdown formatting"""
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        content = re.sub(r'_([^_]+)_', r'\1', content)
        content = re.sub(r'~~([^~]+)~~', r'\1', content)
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
        content = re.sub(r'`([^`]+)`', r'\1', content)
        return content


if __name__ == "__main__":
    # Test
    import os
    from dotenv import load_dotenv
    load_dotenv()

    logging.basicConfig(level=logging.INFO)
    api_key = os.getenv('GEMINI_API_KEY')

    if api_key:
        generator = LeetCodeSolutionGenerator(api_key)
        test_problem = {'id': 1, 'title': 'Two Sum'}

        result = generator.generate_complete_solution(test_problem)
        if result:
            print("=== PYTHON ===")
            print(result['python_code'][:200])
            print("\n=== TYPESCRIPT ===")
            print(result['typescript_code'][:200])
            print("\n=== EXPLANATION ===")
            print(result['explanation'][:300])
