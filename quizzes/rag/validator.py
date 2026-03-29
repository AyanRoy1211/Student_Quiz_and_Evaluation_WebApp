# quizzes/rag/validator.py

from .embedder import cosine_similarity

DUPLICATE_THRESHOLD = 0.85


def check_structure(questions: list[dict]) -> list[str]:
    """
    Validate structural integrity of generated questions.
    Returns a list of issue strings. Empty list means all clear.

    Checks:
    - Each question has a non-empty 'text' field
    - Each question has exactly 4 choices
    - Each question has exactly 1 correct choice
    """
    issues = []

    for i, q in enumerate(questions):
        label = f"Question {i + 1}"

        if not q.get('text', '').strip():
            issues.append(f"{label}: question text is empty.")

        choices = q.get('choices', [])

        if len(choices) != 4:
            issues.append(
                f"{label}: has {len(choices)} choices — exactly 4 required."
            )

        correct_count = sum(1 for c in choices if c.get('is_correct') is True)

        if correct_count == 0:
            issues.append(f"{label}: no correct answer marked.")
        elif correct_count > 1:
            issues.append(
                f"{label}: {correct_count} choices marked correct — exactly 1 required."
            )

    return issues


def check_duplicates(questions: list[dict]) -> list[str]:
    """
    Detect near-duplicate questions using cosine similarity.
    Any pair scoring above DUPLICATE_THRESHOLD is flagged.

    Returns a list of issue strings describing duplicate pairs.
    """
    issues = []
    texts = [q.get('text', '') for q in questions]

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if not texts[i] or not texts[j]:
                continue
            similarity = cosine_similarity(texts[i], texts[j])
            if similarity >= DUPLICATE_THRESHOLD:
                issues.append(
                    f"Questions {i + 1} and {j + 1} are too similar "
                    f"(similarity: {similarity:.2f}). Remove or rephrase one."
                )

    return issues


def deduplicate(questions: list[dict]) -> list[dict]:
    """
    Automatically remove duplicate questions rather than flagging them.
    Keeps the first occurrence, drops subsequent duplicates.
    Used in the auto-fix retry path.
    """
    kept = []
    kept_texts = []

    for q in questions:
        text = q.get('text', '')
        is_duplicate = False

        for kept_text in kept_texts:
            if cosine_similarity(text, kept_text) >= DUPLICATE_THRESHOLD:
                is_duplicate = True
                break

        if not is_duplicate:
            kept.append(q)
            kept_texts.append(text)

    return kept


def validate(questions: list[dict]) -> tuple[bool, list[str]]:
    """
    Run full validation — structural checks then duplicate detection.
    Returns (is_valid, issues) where is_valid is True only if issues is empty.
    """
    issues = check_structure(questions)
    issues += check_duplicates(questions)
    return len(issues) == 0, issues