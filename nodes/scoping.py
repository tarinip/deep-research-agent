import json
from datetime import date
from typing import Dict, Any
from my_llm.ollama_client import chat_with_llm
from utils.json_sanitizer import sanitize_json_string
from core.template_parser import ResearchTemplateLoader
from utils.db_manager import save_mission_to_db 

ResearchState = Dict[str, Any]

def scoping_and_clarification(state: ResearchState, depth=0) -> (ResearchState, str):
    user_query = state.get("user_query", "")
    
    # 1. DYNAMIC DISCOVERY
    # Initialize the loader to see what folders (domains) and files (templates) we have
    loader = ResearchTemplateLoader()
    domain_map = loader.get_domain_map() 

    # 2. THE MULTI-SELECT PROMPT
    # We explicitly tell the LLM it can choose a LIST of templates
    system_prompt = f"""
You are a master Scoping Module for a Deep Research Agent.
Your goal is to categorize the user's request into a DOMAIN and one or more TEMPLATES.

Available Domains & Templates:
{json.dumps(domain_map, indent=2)}

Rules:
1. Identify the 'target' (the specific entity, city, or topic).
2. Choose the correct 'domain' from the list.
3. Choose the 'templates' (MUST be an array/list). 
   - Select ONE template for simple queries.
   - Select MULTIPLE templates if the query has overlapping needs (e.g., "A luxury trip with kids" -> ["luxury", "family_kids"]).
4. If the query is vague, set 'clarification_needed' to true and ask a 'clarification_question'.
5. Output ONLY JSON in <json></json> tags.

JSON Structure:
{{
  "clarification_needed": bool,
  "clarification_question": string,
  "domain": string,
  "templates": ["template_name_1", "template_name_2"],
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

    # 4. LOAD & MERGE DOMAIN-SPECIFIC TEMPLATES
    # We now handle the case where the LLM picks multiple templates
    try:
        selected_templates = parsed.get("templates", ["general"])
        target_entity = parsed.get("target")
        domain_name = parsed.get("domain")

        # We use a merge-capable loader method
        research_brief = loader.load_multiple_from_domain(
            domain=domain_name,
            templates=selected_templates, 
            target=target_entity
        )
        
        state["research_brief"] = research_brief
        state["active_domain"] = domain_name
        state["selected_templates"] = selected_templates # Helpful for debugging
        
    except Exception as e:
        print(f"❌ Template Merging Failed: {e}")
        # Fallback to clarification if the templates don't exist or fail to load
        parsed["clarification_needed"] = True
        parsed["clarification_question"] = "I had trouble loading the research tracks for that domain. Could you be more specific?"
        state["scoping_result"] = parsed
        return state, "clarification_needed"

    # 5. PERSISTENCE (POSTGRES)
    try:
        # Join templates into a string (e.g., "luxury, family_kids") for the DB column
        template_str = ", ".join(selected_templates)
        
        mission_id = save_mission_to_db(
            user_query=user_query,
            target=target_entity,
            template=template_str,
            research_brief=research_brief,
            domain=domain_name
        )
        state["mission_id"] = mission_id
        print(f"💾 {domain_name.upper()} Mission Saved (ID: {mission_id}) | Templates: {template_str}")
        
    except Exception as db_err:
        # We don't stop the agent if the DB fails, but we warn the console
        print(f"⚠️ DB Warning: {db_err}")

    # Add the final confirmation to the message history
    state.setdefault("messages", []).append({
        "role": "system", 
        "content": parsed.get("confirmation_message", f"Starting {domain_name} research on {target_entity}...")
    })

    return state, "research_brief"