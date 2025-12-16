# utils/json_sanitizer.py

import json, ast, re

def sanitize_json_string(text):
    """Extract valid JSON from messy LLM output. Accepts strings or dicts."""

    # If text is already a dict → just return it
    if isinstance(text, dict):
        return text

    # Force conversion to string for safety
    if not isinstance(text, str):
        text = str(text)

    def ensure_braces(t: str) -> str:
        """Wrap text in {} if missing."""
        t = t.strip()
        if not t.startswith("{"):
            t = "{" + t
        if not t.endswith("}"):
            t = t + "}"
        return t

    def extract_braced(t):
        start = t.find('{')
        if start == -1:
            return None

        stack = []
        for i in range(start, len(t)):
            if t[i] == '{':
                stack.append('{')
            elif t[i] == '}':
                stack.pop()
                if not stack:
                    return t[start:i+1]
        return None

    json_str = extract_braced(text)
    if not json_str:
        json_str = ensure_braces(text)  # wrap whole text in braces

    cleaned = re.sub(r"```json|```", "", json_str).strip()

    # Attempt normal JSON load
    try:
        return json.loads(cleaned)
    except Exception:
        # Attempt literal python dict parsing
        try:
            return ast.literal_eval(cleaned)
        except Exception:
            # Final fallback: wrap and try again
            cleaned = ensure_braces(cleaned)
            try:
                return json.loads(cleaned)
            except Exception:
                return {"error": "parse_fail", "raw": cleaned}
