# import json
# import uuid
# from typing import Dict, Any, Tuple
# from my_llm.ollama_client import chat_with_llm
# from utils.json_sanitizer import sanitize_json_string
# from nodes.research import run_fast_research, run_deep_research 
# # For Deep Mode persistence
# import psycopg2
# from datetime import datetime
# ResearchState = Dict[str, Any]

# def scoping_and_clarification(state: ResearchState) -> Tuple[ResearchState, str]:
#     user_query = state.get("user_query", "")
#     current_date = datetime.now().strftime("%B %d, %Y")
#     system_prompt = f"""
# You are the Lead Travel Consultant and Scoping Intelligence. 
# CURRENT DATE: {current_date}

# ### MISSION
# Evaluate the user's travel request. Your goal is to move from a "vague destination" to a "detailed itinerary brief." 

# ### THE COMPLETENESS CHECKLIST
# To avoid generating a generic/boring itinerary, you MUST ensure the query contains at least THREE dimensions of data. If it has fewer, you must clarify.
# 1. **LOCATION**: A specific city, region, or country.
# 2. **TEMPORAL**: When are they going? For how long?
# 3. **PARAMETRIC**: Budget (e.g., luxury/budget), Group (e.g., family/solo), or Interests (e.g., food/history).

# ### INSTRUCTIONS
# - **Broad Queries**: If the user provides only a location (e.g., "trip to Singapore"), set `clarification_needed` to true.
# - **Specific Queries**: If they provide location + dates or location + budget, you may set it to false.
# - **Tone**: Always be professional, inviting, and travel-oriented.

# ### OUTPUT JSON SCHEMA
# {{
#   "reasoning": "Explain which dimensions (Location, Temporal, Parametric) are present or missing.",
#   "research_mode": "fast" | "deep",
#   "target": "The destination name",
#   "domain": "travel",
#   "templates": ["Select relevant: luxury, budget, family, solo, adventure, or general"],
#   "fast_tasks": ["Only if mode is fast: 3-4 quick search queries"],
#   "clarification_needed": boolean,
#   "clarification_question": "A friendly response asking for the specific missing dimensions."
# }}
# """

#     # 1. Call LLM to Route
#     raw_response = chat_with_llm(system_prompt=system_prompt, user_prompt=user_query)
#     scoping_result = sanitize_json_string(raw_response)
    
#     # 2. Update State
#     state["research_mode"] = scoping_result.get("research_mode", "fast")
#     state["target"] = scoping_result.get("target", "subject")
#     state["active_domain"] = scoping_result.get("domain", "general")
#     state["scoping_result"] = scoping_result

#     # 3. Handle Branching Logic
#     if scoping_result.get("clarification_needed"):
#         return state, "clarification_needed"

#     if state["research_mode"] == "fast":
#         # BYPASS: Directly set sub_questions so research node can start immediately
#         state["sub_questions"] = scoping_result.get("fast_tasks", [user_query])
#         print(f"⚡ Fast Route Selected. Tasks: {len(state['sub_questions'])}")
#         return state, "fast_research" # This string must match your graph edge

#     else:
#         # DEEP ROUTE: Initialize Postgres Mission for persistence
#         print(f"🧪 Deep Route Selected. Templates: {scoping_result.get('templates')}")
#         mission_id = _create_postgres_mission(state, scoping_result)
#         state["mission_id"] = mission_id
#         return state, "research_brief"

# def _create_postgres_mission(state: ResearchState, scoping: Dict) -> int:
#     try:
#         conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
#         cur = conn.cursor()
        
#         # We use COALESCE-style logic to ensure we don't send None to the DB
#         query_text = state.get("user_query", "No Query")
#         domain_text = scoping.get("domain", "general")
#         mission_uuid = uuid.uuid4()
        
#         cur.execute(
#             "INSERT INTO research_missions (id, user_query, domain, status) VALUES (%s, %s, %s, 'scoped') RETURNING id",
#             (str(mission_uuid), query_text, domain_text)
#         )
        
#         m_id = cur.fetchone()[0]
#         conn.commit()
#         cur.close()
#         conn.close()
#         print(f"✅ DB Success: Generated Mission ID {m_id}")
#         return m_id
#     except Exception as e:
#         # Check your terminal for this specific message!
#         print(f"❌ DB Mission Creation Failed: {e}")
#         return None
import json
import uuid
from typing import Dict, Any, Tuple
from datetime import datetime
from my_llm.ollama_client import chat_with_llm
from utils.json_sanitizer import sanitize_json_string
import psycopg2

ResearchState = Dict[str, Any]

def scoping_and_clarification(state: ResearchState) -> Tuple[ResearchState, str]:
    # 1. CONTEXT STITCHING: Combine original intent with new details
    user_input = state.get("user_query", "")
    original = state.get("original_query", "")

    if original and original.lower() not in user_input.lower():
        # If we have a stored original query, merge it for the LLM
        full_context_query = f"ORIGINAL INTENT: {original} | ADDITIONAL DETAILS: {user_input}"
    else:
        # First time running: set the original query
        full_context_query = user_input
        state["original_query"] = user_input

    current_date = datetime.now().strftime("%B %d, %Y")

    # 2. TRAVEL-SPECIFIC SCOPING PROMPT
    system_prompt = f"""
    You are a Senior Travel Consultant and Research Router. you need to decide which mode to be chosen
    CURRENT DATE: {current_date}
    1. FAST MODE: Use for simple lookups, recommendations, or quick facts. 
       - If Fast, generate 3-4 specific search queries (fast_tasks).
    2. DEEP MODE: Use for complex analysis, detailed travel planning, or multi-step research.
       - If Deep, select appropriate templates (e.g., luxury_travel, budget_travel, general).

    ### YOUR MISSION:
    Analyze the user's query and decide if we have enough information to build a high-quality travel brief.

   
  

    ### CONTEXT SWITCHING RULE:
    - If the 'ADDITIONAL DETAILS' mentions a DIFFERENT city/country than the 'ORIGINAL INTENT', prioritize the NEW city.
    - If the NEW city is part of a specific question (e.g., "Best time to visit Bali"), set "research_mode": "fast" and "clarification_needed": false.
    - Do NOT ask for details about the old city if the user has moved on.

    ### DECISION LOGIC:
    - If dimensions are missing: set "clarification_needed": true.
    - If all 3 dimensions are present: set "clarification_needed": false.
    - For simple facts (e.g., "Visa for Singapore?"): use research_mode: "fast".
    - For planning trips: use research_mode: "deep".

    ### OUTPUT ONLY JSON:
    {{
      "reasoning": "Briefly explain which dimensions are found and which are missing.",
      "research_mode": "fast" | "deep",
      "target": "The destination city/country",
      "domain": "travel",
      "templates": ["Select relevant: luxury, budget, family, solo, adventure, general"],
      "clarification_needed": boolean,
      "clarification_question": "If true, ask a friendly question for the SPECIFIC missing info."
    }}
    """

    # 3. CALL LLM
    raw_response = chat_with_llm(system_prompt=system_prompt, user_prompt=full_context_query)
    scoping_result = sanitize_json_string(raw_response)
    
    # 4. UPDATE STATE
    state["research_mode"] = scoping_result.get("research_mode", "deep")
    state["target"] = scoping_result.get("target", "Unknown")
    state["active_domain"] = scoping_result.get("domain", "travel")
    state["scoping_result"] = scoping_result
    state["clarification_needed"] = scoping_result.get("clarification_needed", False)

    # 5. BRANCHING LOGIC
    if state["clarification_needed"]:
        state["clarification_question"] = scoping_result.get("clarification_question", "Could you provide more details?")
        print(f"❓ Clarification Required: {state['clarification_question']}")
        return state, "clarification_needed"

    if state["research_mode"] == "fast":
        state["sub_questions"] = scoping_result.get("fast_tasks", [user_input])
        return state, "fast_research"

    else:
        # DEEP ROUTE: Persist to DB
        print(f"🧪 Deep Route Selected for {state['target']}. Templates: {scoping_result.get('templates')}")
        mission_id = _create_postgres_mission(state, scoping_result)
        state["mission_id"] = mission_id
        return state, "research_brief"

def _create_postgres_mission(state: ResearchState, scoping: Dict) -> str:
    try:
        # Note: In production, use a connection pool or env variables
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        cur = conn.cursor()
        
        query_text = state.get("original_query", "No Query")
        domain_text = scoping.get("domain", "travel")
        mission_uuid = str(uuid.uuid4())
        
        cur.execute(
            "INSERT INTO research_missions (id, user_query, domain, status) VALUES (%s, %s, %s, 'scoped') RETURNING id",
            (mission_uuid, query_text, domain_text)
        )
        
        m_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return m_id
    except Exception as e:
        print(f"❌ DB Mission Creation Failed: {e}")
        return str(uuid.uuid4()) # Fallback ID to keep the graph moving