# quizzes/rag/generator.py

import json
import google.generativeai as genai
from django.conf import settings


def _get_client():
    """Configure and return the Gemini client."""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-2.5-flash')


def call_gemini(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the raw text response.
    Raises an exception if the API call fails.
    """
    model = _get_client()
    response = model.generate_content(prompt)
    return response.text


def parse_gemini_response(raw_response: str) -> list[dict]:
    """
    Parse Gemini's raw text response into a list of question dicts.

    Handles cases where Gemini wraps output in markdown code fences
    despite being told not to — a common LLM behaviour.

    Returns a list of dicts, each with keys:
        'text'    -> str (question text)
        'choices' -> list of {'text': str, 'is_correct': bool}
    """
    # Strip markdown code fences if present
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split('\n')
        # Remove first line (```json or ```) and last line (```)
        cleaned = '\n'.join(lines[1:-1])

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\n\nRaw response:\n{raw_response}")

    if 'questions' not in data:
        raise ValueError("Gemini response missing 'questions' key.")

    return data['questions']


def generate_questions(prompt: str, max_retries: int = 2) -> tuple[list[dict], list[str]]:
    """
    Call Gemini with the given prompt and parse the response.
    Returns (questions, errors) where errors is an empty list on success.

    Does NOT handle validation here — that's the validator's job.
    This function only handles API call failures and JSON parse errors.
    """
    errors = []

    for attempt in range(max_retries + 1):
        try:
            raw = call_gemini(prompt)
            questions = parse_gemini_response(raw)
            return questions, []
        except ValueError as e:
            errors.append(str(e))
            if attempt == max_retries:
                break
        except Exception as e:
            errors.append(f"Gemini API error: {str(e)}")
            if attempt == max_retries:
                break

    return [], errors