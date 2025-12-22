# # # nodes/scoping.py

# # from datetime import date
# # from typing import Dict, Any
# # from my_llm.ollama_client import ollama_chat
# # from utils.json_sanitizer import sanitize_json_string
# # from core.template_parser import ResearchTemplateLoader # <-- NEW IMPORT

# # ResearchState = Dict[str, Any]

# # def scoping_and_clarification(state: ResearchState, depth=0) -> (ResearchState, str):
# #     user_query = state["user_query"]
# #     today = date.today()
# #     current_date = today.strftime("%Y-%m-%d")
    
# #     # 1. NEW: Discover available templates for the LLM to choose from
# #     loader = ResearchTemplateLoader()
# #     available_templates = loader.list_templates() # e.g. ['competitor_analysis', 'tech_audit']

# #     system_prompt = f"""
# # You are a scoping module for a deep research agent.
# # Your task is to:
# # 1. Determine if the query is clear.
# # 2. If clear, identify the SUBJECT (target) and the RESEARCH TRACK.

# # Available Research Tracks: {available_templates}

# # Rules:
# # - If clarification is NOT needed, you MUST identify the 'target' (the company/topic) and the 'template' to use.
# # - Output ONLY JSON in <json></json> tags.

# # JSON Keys:
# # - "clarification_needed": boolean
# # - "clarification_question": string
# # - "confirmation_message": string
# # - "target": string (The entity to research, e.g., "Tesla")
# # - "template": string (Must be one of: {available_templates})
# # """

# #     user_prompt = f"User Query: {user_query}\nExtract the target and choose the best template."

# #     # ---- CALL OLLAMA ----
# #     raw = ollama_chat(system_prompt=system_prompt, user_prompt=user_prompt)
# #     parsed = sanitize_json_string(raw)

# #     # Fallback if parsing fails
# #     if not isinstance(parsed, dict):
# #         parsed = {"clarification_needed": True, "clarification_question": "I couldn't process that. Please rephrase."}

# #     state["scoping_result"] = parsed

# #     # ---- Handle clarification ----
# #     if parsed.get("clarification_needed", False):
# #         state.setdefault("messages", []).append({"role": "assistant", "content": parsed.get("clarification_question")})
# #         if depth >= 3:
# #             return state, "research_brief" 
# #         return state, "clarification_needed" 

# #     # ---- NEW: INITIALIZE THE RESEARCH BRIEF ----
# #     # This is where scoping ends and the product logic begins
# #     print(f"✅ Target Identified: {parsed.get('target')}")
# #     print(f"📂 Template Selected: {parsed.get('template')}")

# #     try:
# #         # We use the loader to create the actual Research Brief
# #         research_brief = loader.load_and_customize(
# #             parsed.get("template"), 
# #             parsed.get("target")
# #         )
# #         # Store the brief in the state for the Research Node to use
# #         state["research_brief"] = research_brief
# #     except Exception as e:
# #         print(f"❌ Template Error: {e}")
# #         return state, "clarification_needed"

# #     state.setdefault("messages", []).append({"role": "system", "content": parsed.get("confirmation_message")})
# #     return state, "research_brief"
# # nodes/scoping.py
# from datetime import date
# from typing import Dict, Any
# from my_llm.ollama_client import chat_with_llm
# from utils.json_sanitizer import sanitize_json_string
# from core.template_parser import ResearchTemplateLoader
# # Import your new DB utility
# from utils.db_manager import save_mission_to_db 

# ResearchState = Dict[str, Any]

# def scoping_and_clarification(state: ResearchState, depth=0) -> (ResearchState, str):
#     user_query = state["user_query"]
#     today = date.today()
#     current_date = today.strftime("%Y-%m-%d")
    
#     loader = ResearchTemplateLoader()
#     available_templates = loader.list_templates()

#     # Inside nodes/scoping.py
#     system_prompt = f"""
# You are a scoping module for a deep research agent.
# Your task is to:
# 1. Determine if the query is clear.
# 2. If clear, identify the SUBJECT (target) and the RESEARCH TRACK.

# Available Research Tracks: {available_templates}
# Rules:
# If clarification is NOT needed, you MUST identify the 'target' (the company/topic) and the 'template' to use.
# Output ONLY JSON in <json></json> tags.

# JSON Keys:
# "clarification_needed": boolean
# "clarification_question": string
# "confirmation_message": string
# "target": string (The entity to research, e.g., "Tesla")
# "template": string (Must be one of: {available_templates})
#  """
#     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"Query: {user_query}")
#     parsed = sanitize_json_string(raw)

#     if not isinstance(parsed, dict) or parsed.get("clarification_needed", True):
#         state["scoping_result"] = parsed
#         return state, "clarification_needed"

#     # ---- LOAD TEMPLATE ----
#     try:
#         research_brief = loader.load_and_customize(
#             parsed.get("template"), 
#             parsed.get("target")
#         )
#         state["research_brief"] = research_brief
#     except Exception as e:
#         return state, "clarification_needed"

#     # ---- NEW: PERSISTENCE LAYER ----
#     # This saves the 'State of Intent' to Postgres
#     try:
#         mission_id = save_mission_to_db(
#             user_query,
#             parsed.get("target"),
#             parsed.get("template"),
#             research_brief
#         )
#         state["mission_id"] = mission_id # Use this ID in all future nodes!
#         print(f"💾 Mission Persisted to Postgres: ID {mission_id}")
#     except Exception as db_err:
#         print(f"⚠️ DB Warning: Could not save mission, continuing in-memory. {db_err}")

#     return state, "research_brief"
from datetime import date
from typing import Dict, Any
import json
from my_llm.ollama_client import chat_with_llm
from utils.json_sanitizer import sanitize_json_string
from core.template_parser import ResearchTemplateLoader
from utils.db_manager import save_mission_to_db 

ResearchState = Dict[str, Any]

def scoping_and_clarification(state: ResearchState, depth=0) -> (ResearchState, str):
    user_query = state["user_query"]
    
    # 1. DYNAMIC DISCOVERY
    # Instead of just listing files, the loader now categorizes by folder
    loader = ResearchTemplateLoader()
    
    # We ask the loader: "What domains (folders) and templates do we have?"
    # Expected structure: {"travel": ["family_kids", "general"], "finance": []}
    domain_map = loader.get_domain_map() 
    available_domains = list(domain_map.keys())

    # 2. THE MULTI-DOMAIN PROMPT
    # We tell the LLM about the structure so it can pick the DOMAIN first
    system_prompt = f"""
You are a master Scoping Module. 
Your goal is to categorize the user's request into a DOMAIN and a TEMPLATE.

Available Domains & Templates:
{json.dumps(domain_map, indent=2)}

Rules:
1. Identify the 'target' (the specific entity, city, or topic).
2. Choose the correct 'domain' from the list.
3. Choose the best 'template' from that domain's list.
4. If the query is vague, set 'clarification_needed' to true and ask a question.
5. Output ONLY JSON in <json></json> tags.

JSON Keys:
{{
  "clarification_needed": bool,
  "clarification_question": string,
  "domain": string,
  "template": string,
  "target": string,
  "confirmation_message": string
}}
"""
    # ---- CALL LLM ----
    raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"Query: {user_query}")
    parsed = sanitize_json_string(raw)

    # 3. VALIDATION & CLARIFICATION
    if not isinstance(parsed, dict) or parsed.get("clarification_needed", True):
        state["scoping_result"] = parsed
        return state, "clarification_needed"

    # 4. LOAD DOMAIN-SPECIFIC TEMPLATE
    try:
        # Note: We now pass 'domain' so the loader knows which folder to look in
        research_brief = loader.load_from_domain(
            domain=parsed.get("domain"),
            template=parsed.get("template"), 
            target=parsed.get("target")
        )
        state["research_brief"] = research_brief
        state["active_domain"] = parsed.get("domain") # Keep track of domain
    except Exception as e:
        print(f"❌ Template Loading Failed: {e}")
        return state, "clarification_needed"

    # 5. PERSISTENCE
    try:
        mission_id = save_mission_to_db(
            user_query,
            parsed.get("target"),
            parsed.get("template"),
            research_brief,
            domain=parsed.get("domain") # Added domain to your DB call
        )
        state["mission_id"] = mission_id
        print(f"💾 {parsed.get('domain').upper()} Mission Saved: ID {mission_id}")
    except Exception as db_err:
        print(f"⚠️ DB Warning: {db_err}")

    return state, "research_brief"