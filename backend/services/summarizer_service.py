def summarize_text(text: str, max_sentences: int = 5) -> str:
    """Placeholder summarizer — replace with your model or API call."""
    if not text:
        return ""
    # naive placeholder: return first N sentences
    sentences = text.split('.')
    short = '.'.join(s for s in sentences[:max_sentences] if s).strip()
    return short + ('.' if short else '')
