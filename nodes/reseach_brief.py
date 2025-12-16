# nodes/research_brief.py

from datetime import datetime
from typing import Dict, Any
import  json

from my_llm.ollama_client import ollama_chat
from utils.json_sanitizer import sanitize_json_string

ResearchState = Dict[str, Any]


def build_research_brief(state: ResearchState) -> (ResearchState, str):

    scoped = state.get("scoping_result", {})
    user_query = state.get("user_query", "")

    system_prompt = """
You are the Research Brief Agent in a Deep Research System.

Your job is to convert the user’s scoped question into a well-structured research brief.
You DO NOT perform any research. You only define the plan.

Return ONLY valid JSON with this structure:

{
  "research_question": "<refined main question>",
  "sub_questions": ["q1", "q2", ...],
  "coverage_depth": "<overview | intermediate | deep research>",
  "must_cover": ["topic1", "topic2"],
  "avoid": ["things to skip"],
  "expected_sources": ["journals", "news", "government data", "books", "expert opinions"],
  "final_output_format": "<report | explanation | comparison | timeline | bullet summary>",
  "constraints": ["if any"],
  "summary": "<1 paragraph summary of the brief>"
}

Rules:
1. NEVER hallucinate facts.
2. NEVER include actual research or answers.
3. Only define the plan.
4. Ensure JSON is clean and machine-parseable.
"""

    user_message = f"""
User Request / Final Scoped Query:
{user_query}

Scoping Output:
{json.dumps(scoped, indent=2)}

Today's date: {datetime.now().strftime("%Y-%m-%d")}
"""

    raw = ollama_chat(system_prompt=system_prompt, user_prompt=user_message)
    print("\n🤖 Raw Research Brief Output:\n", raw)

    parsed = sanitize_json_string(raw)

    # fail-safe
    if not isinstance(parsed, dict):
        parsed = {
            "research_question": user_query,
            "sub_questions": [],
            "coverage_depth": "overview",
            "must_cover": [],
            "avoid": [],
            "expected_sources": [],
            "final_output_format": "report",
            "constraints": [],
            "summary": "Auto-generated fallback research brief."
        }

    state["research_brief"] = parsed
    return state, "research"   # Next node → actual Research Engine
