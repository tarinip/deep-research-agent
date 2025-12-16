
# nodes/scoping.py

from datetime import date
from typing import Dict, Any
import sys
import pathlib
import json

# Add my_llm and utils to path
# sys.path.append(str(pathlib.Path(__file__).parent.parent / "my_llm"))
# sys.path.append(str(pathlib.Path(__file__).parent.parent / "utils"))

from my_llm.ollama_client import ollama_chat
from utils.json_sanitizer import sanitize_json_string

ResearchState = Dict[str, Any]


# ===============================
# SCOPING + CLARIFICATION NODE
# ===============================
def scoping_and_clarification(state: ResearchState, depth=0) -> (ResearchState, str):

    user_query = state["user_query"]
    today = date.today()
    current_date = today.strftime("%Y-%m-%d")
    messages = state.get("messages", [])
    history_parts = []
    for msg in messages:
    # Safely extract role and content, handling potential missing keys
        role = msg.get("role", "system").upper()
        content = msg.get("content", "...")
        history_parts.append(f"[{role}]: {content}")

    messages_str = '\n\n'.join(history_parts)
    # messages_str = '\n\n'.join(messages)
    system_prompt = f"""
You are a scoping and clarification module for a deep research agent.
Your task is to determine whether the user's query is sufficiently clear to begin research.

Today's date: {current_date} (YYYY-MM-DD)

You will receive the entire message history between the user and the agent:
{messages_str}

Rules:
1. Decide whether clarification is needed.
2. If clarification IS needed, generate ONLY ONE clarification question.
   - A second clarification question should be generated only in extremely rare cases
     (only if the user query is fundamentally impossible to interpret without it).
3. If clarification is NOT needed, generate a confirmation message that clearly states
   the research will now begin.
4. Your output MUST be wrapped in <json></json> tags.
5. The JSON you produce MUST have the following keys:
   - "clarification_needed": boolean
   - "clarification_question": string (empty if no clarification needed)
   - "confirmation_message": string (empty if clarification is needed)
6. Keep your reasoning internal. Only produce the JSON described above.
"""
    user_prompt = f"""
The user has asked the following question:

"{user_query}"

Determine whether the question is clear enough to begin research or if clarification is needed.
Follow all rules and output ONLY the required JSON wrapped in <json> tags.
"""


    # ---- CALL OLLAMA ----
    raw = ollama_chat(system_prompt=system_prompt, user_prompt=user_prompt)
    print("\n🤖 Raw Ollama Output:\n", raw)

    # ---- Sanitize JSON ----
    parsed = sanitize_json_string(raw)

    # fallback if parsing failed
    if not isinstance(parsed, dict):
        parsed = {
            "need_clarification": True,
            "question": "Please clarify your request.",
            "verification": ""
        }

    state["scoping_result"] = parsed
    #state.setdefault("messages", []).append(parsed)

    # ---- Handle clarification ----
    if parsed.get("clarification_needed", False):
        state.setdefault("messages", []).append({"role": "assistant", "content": parsed.get("clarification_question", "Please clarify.")})
    else:
        state.setdefault("messages", []).append({"role": "system", "content": parsed.get("confirmation_message", "Scoping complete.")})


    # ---- Handle clarification ----
    if parsed.get("clarification_needed", False):

        if depth >= 3: # Increase depth check to 3 for 4 cycles (0, 1, 2, 3) if needed, or keep at 2 for 3 cycles (0, 1, 2)
            print("\n⚠️ Max clarification cycles reached.")
            # If max cycles reached, force proceeding to research brief
            return state, "research_brief" 

        # --- IMPORTANT FIX: RETURN SIGNAL ---
        # Do NOT ask the user or recurse here. We just signal the Graph to END 
        # so the runner can pause and get the user's input.
        print("\n🧠 LLM decided clarification is needed. Signaling END.")
        
        # The runner function (run_deep_research) will handle the user input/loop
        return state, "clarification_needed" 

    # ---- No clarification → done ----
    print("\n✅ Verified:", parsed.get("confirmation_message"))
    return state, "research_brief"
