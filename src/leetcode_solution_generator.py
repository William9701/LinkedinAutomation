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
- CRITICAL RULE: ONLY write comments that start EXACTLY with "# Step 1:", "# Step 2:", etc.
- DO NOT write ANY other comments - not on the same line as code, not anywhere else
- Each "# Step X:" comment must be on its own separate line
- Use self-explanatory variable names
- Keep it under 25 lines
- Example (FOLLOW THIS EXACTLY):
```python
def functionName(params):
    # Step 1: Initialize counter
    count = 0

    # Step 2: Process each item
    for item in items:
        count += item

    # Step 3: Return result
    return count
```

=== TYPESCRIPT CODE REQUIREMENTS ===
- Equivalent TypeScript solution
- CRITICAL RULE: ONLY write comments that start EXACTLY with "// Step 1:", "// Step 2:", etc.
- DO NOT write ANY other comments - not on the same line as code, not anywhere else
- Each "// Step X:" comment must be on its own separate line
- Use proper TypeScript types
- Example (FOLLOW THIS EXACTLY):
```typescript
function functionName(params: type[]): returnType {{
    // Step 1: Initialize counter
    let count: number = 0;

    // Step 2: Process each item
    for (const item of items) {{
        count += item;
    }}

    // Step 3: Return result
    return count;
}}
```

=== EXPLANATION REQUIREMENTS ===
CRITICAL: Your ENTIRE explanation must be MAXIMUM 2200 characters. LinkedIn limit is 3000 but we need safety margin.

WRITE A SUPER CONCISE EXPLANATION:

🎯 THE PROBLEM (30-50 words max)
One sentence with analogy. That's it.

💡 THE IDEA (50-80 words max)
What's the core strategy in plain English?

📝 QUICK EXAMPLE (100-150 words max)
Tiny example: nums=[2,7,11,15], target=9
Show 3 steps:
"Step 1: Empty dict
Step 2: See 2, need 7, save 2
Step 3: See 7, found it!"

⚡ WHY IT WORKS (40-60 words max)
The insight + Time O(?) Space O(?)

🎓 TIP (20-30 words max)
One pattern to remember

ABSOLUTE REQUIREMENTS:
- TOTAL LENGTH: 1800-2200 characters MAX
- Count your characters as you write!
- NO markdown formatting
- Use emojis for headers
- Be BRIEF and punchy
- Twitter thread style
- If you write more than 2200 chars, STOP and cut content

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

            # Smart truncation for LinkedIn (max 3000, target 2400)
            if len(explanation) > 2400:
                logger.warning(f"Explanation too long ({len(explanation)} chars), smartly truncating to 2400")
                # Find last complete sentence before 2350 chars
                truncate_point = 2350
                last_period = explanation.rfind('.', 0, truncate_point)
                last_exclaim = explanation.rfind('!', 0, truncate_point)
                last_question = explanation.rfind('?', 0, truncate_point)

                end_point = max(last_period, last_exclaim, last_question)
                if end_point > 2000:  # Only truncate at sentence if it's reasonable
                    explanation = explanation[:end_point + 1]
                else:
                    explanation = explanation[:2397] + "..."

            logger.info(f"Generated complete solution for: {problem['title']} ({len(explanation)} chars)")
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
