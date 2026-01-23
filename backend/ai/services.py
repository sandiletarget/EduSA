"""AI service layer (placeholder).

This module isolates AI logic so it can be swapped with real providers later.
"""
from collections import Counter

from backend.live_class.models import TranscriptSegment


def build_summary(live_class_id):
    segments = TranscriptSegment.objects.filter(live_class_id=live_class_id).values_list("text", flat=True)
    joined = " ".join(segments)
    if not joined:
        return "No transcript yet."
    words = [w.strip(".,!?;:").lower() for w in joined.split() if len(w) > 4]
    keywords = [word for word, _ in Counter(words).most_common(5)]
    bullets = "\n".join([f"• {kw.title()}" for kw in keywords])
    return bullets or "Summary pending."


def suggest_answer(question, transcript_snippets):
    if not transcript_snippets:
        return "I need more context. I will flag this question for the teacher."
    return "Based on today's lesson, remember the definition and try applying it to a simple example."  # placeholder


def detect_flags(text):
    flagged_terms = {"abuse", "hate", "insult"}
    lowered = text.lower()
    for term in flagged_terms:
        if term in lowered:
            return True, f"Flagged term: {term}"
    return False, ""
