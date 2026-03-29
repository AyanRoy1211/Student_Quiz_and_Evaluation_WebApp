# quizzes/rag/prompt_builder.py

import json


DIFFICULTY_INSTRUCTIONS = {
    'easy': (
        "Questions should test basic recall and simple understanding. "
        "Use straightforward language. Avoid trick questions."
    ),
    'medium': (
        "Questions should test application and comprehension. "
        "Include some questions that require reasoning, not just recall."
    ),
    'hard': (
        "Questions should test deep understanding, analysis, and critical thinking. "
        "Include nuanced distractors that require careful consideration to eliminate."
    ),
}

OUTPUT_SCHEMA = {
    "questions": [
        {
            "text": "The full question text goes here?",
            "choices": [
                {"text": "Option A", "is_correct": False},
                {"text": "Option B", "is_correct": True},
                {"text": "Option C", "is_correct": False},
                {"text": "Option D", "is_correct": False},
            ]
        }
    ]
}


def build_prompt(
    topic: str,
    difficulty: str,
    num_questions: int,
    context_chunks: list[str] = None,
) -> str:
    """
    Dynamically build the Gemini prompt.

    If context_chunks are provided (from RAG retrieval), the prompt
    instructs Gemini to ground questions in that material.
    If no chunks are provided (no PDF uploaded), Gemini uses general knowledge.
    """
    difficulty_key = difficulty.lower()
    difficulty_instruction = DIFFICULTY_INSTRUCTIONS.get(
        difficulty_key, DIFFICULTY_INSTRUCTIONS['medium']
    )

    context_section = ""
    if context_chunks:
        joined_context = "\n\n---\n\n".join(context_chunks)
        context_section = f"""
## Source Material
The following excerpts are from the instructor's uploaded document.
Base your questions primarily on this content:

{joined_context}

---
"""

    schema_str = json.dumps(OUTPUT_SCHEMA, indent=2)

    prompt = f"""You are an expert quiz designer for an educational platform.

Your task is to generate exactly {num_questions} multiple-choice questions on the topic: **{topic}**

## Difficulty Level: {difficulty.capitalize()}
{difficulty_instruction}
{context_section}
## Rules
- Each question must have exactly 4 answer choices.
- Exactly one choice must have "is_correct": true. All others must be false.
- Questions must be clearly worded and unambiguous.
- Do not repeat or paraphrase the same question more than once.
- Do not include explanations, preamble, or markdown formatting outside the JSON.
- Return ONLY valid JSON. No code fences, no extra text.

## Required Output Format
{schema_str}

Now generate {num_questions} questions on: {topic}
"""
    return prompt.strip()


def build_retry_prompt(original_prompt: str, issues: list[str]) -> str:
    """
    If the first generation fails validation, build a corrective retry prompt
    that tells Gemini exactly what went wrong.
    """
    issues_str = "\n".join(f"- {issue}" for issue in issues)

    retry_prompt = f"""Your previous response had the following issues that must be fixed:

{issues_str}

Please regenerate the quiz, strictly fixing all of the above issues.
Return ONLY valid JSON in the exact format specified. No explanations.

Original instructions:
{original_prompt}
"""
    return retry_prompt.strip()