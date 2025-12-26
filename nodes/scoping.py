# # # import json
# # # from datetime import date
# # # from typing import Dict, Any
# # # from my_llm.ollama_client import chat_with_llm
# # # from utils.json_sanitizer import sanitize_json_string
# # # from core.template_parser import ResearchTemplateLoader
# # # from utils.db_manager import save_mission_to_db 

# # # ResearchState = Dict[str, Any]

# # # def scoping_and_clarification(state: ResearchState, depth=0) -> (ResearchState, str):
# # #     user_query = state.get("user_query", "")
    
# # #     # 1. DYNAMIC DISCOVERY
# # #     # Initialize the loader to see what folders (domains) and files (templates) we have
# # #     loader = ResearchTemplateLoader()
# # #     domain_map = loader.get_domain_map() 

# # #     # 2. THE MULTI-SELECT PROMPT
# # #     # We explicitly tell the LLM it can choose a LIST of templates
# # #     system_prompt = f"""
# # # You are a master Scoping Module for a Deep Research Agent.
# # # Your goal is to categorize the user's request into a DOMAIN and one or more TEMPLATES.

# # # Available Domains & Templates:
# # # {json.dumps(domain_map, indent=2)}

# # # Rules:
# # # 1. Identify the 'target' (the specific entity, city, or topic).
# # # 2. Choose the correct 'domain' from the list.
# # # 3. Choose the 'templates' (MUST be an array/list). 
# # #    - Select ONE template for simple queries.
# # #    - Select MULTIPLE templates if the query has overlapping needs (e.g., "A luxury trip with kids" -> ["luxury", "family_kids"]).
# # # 4. If the query is vague, set 'clarification_needed' to true and ask a 'clarification_question'.
# # # 5. Output ONLY JSON in <json></json> tags.

# # # JSON Structure:
# # # {{
# # #   "clarification_needed": bool,
# # #   "clarification_question": string,
# # #   "domain": string,
# # #   "templates": ["template_name_1", "template_name_2"],
# # #   "target": string,
# # #   "confirmation_message": string
# # # }}
# # # """
# # #     # ---- CALL LLM ----
# # #     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"Query: {user_query}")
# # #     parsed = sanitize_json_string(raw)

# # #     # 3. VALIDATION & CLARIFICATION
# # #     if not isinstance(parsed, dict) or parsed.get("clarification_needed", True):
# # #         state["scoping_result"] = parsed
# # #         return state, "clarification_needed"

# # #     # 4. LOAD & MERGE DOMAIN-SPECIFIC TEMPLATES
# # #     # We now handle the case where the LLM picks multiple templates
# # #     try:
# # #         selected_templates = parsed.get("templates", ["general"])
# # #         target_entity = parsed.get("target")
# # #         domain_name = parsed.get("domain")

# # #         # We use a merge-capable loader method
# # #         research_brief = loader.load_multiple_from_domain(
# # #             domain=domain_name,
# # #             templates=selected_templates, 
# # #             target=target_entity
# # #         )
        
# # #         state["research_brief"] = research_brief
# # #         state["active_domain"] = domain_name
# # #         state["selected_templates"] = selected_templates # Helpful for debugging
        
# # #     except Exception as e:
# # #         print(f"❌ Template Merging Failed: {e}")
# # #         # Fallback to clarification if the templates don't exist or fail to load
# # #         parsed["clarification_needed"] = True
# # #         parsed["clarification_question"] = "I had trouble loading the research tracks for that domain. Could you be more specific?"
# # #         state["scoping_result"] = parsed
# # #         return state, "clarification_needed"

# # #     # 5. PERSISTENCE (POSTGRES)
# # #     try:
# # #         # Join templates into a string (e.g., "luxury, family_kids") for the DB column
# # #         template_str = ", ".join(selected_templates)
        
# # #         mission_id = save_mission_to_db(
# # #             user_query=user_query,
# # #             target=target_entity,
# # #             template=template_str,
# # #             research_brief=research_brief,
# # #             domain=domain_name
# # #         )
# # #         state["mission_id"] = mission_id
# # #         print(f"💾 {domain_name.upper()} Mission Saved (ID: {mission_id}) | Templates: {template_str}")
        
# # #     except Exception as db_err:
# # #         # We don't stop the agent if the DB fails, but we warn the console
# # #         print(f"⚠️ DB Warning: {db_err}")

# # #     # Add the final confirmation to the message history
# # #     state.setdefault("messages", []).append({
# # #         "role": "system", 
# # #         "content": parsed.get("confirmation_message", f"Starting {domain_name} research on {target_entity}...")
# # #     })

# # #     return state, "research_brief"
# # import json
# # from typing import Dict, Any
# # from my_llm.ollama_client import chat_with_llm
# # from utils.json_sanitizer import sanitize_json_string
# # from core.template_parser import ResearchTemplateLoader
# # from utils.db_manager import save_mission_to_db 

# # def scoping_and_clarification(state: Dict[str, Any], depth=0):
# #     user_query = state["user_query"]
# #     loader = ResearchTemplateLoader()
# #     domain_map = loader.get_domain_map() 

# #     system_prompt = f"""
# # You are a Scoping Module for a Deep Research Agent.
# # Your task: Match the user query to a Domain and Template. If no template fits, CREATE a custom one.

# # AVAILABLE TAXONOMY:
# # {json.dumps(domain_map, indent=2)}

# # ### INSTRUCTIONS:
# # 1. **Match**: If a template fits, return its name.
# # 2. **Generate**: If NO template fits (e.g., "Vegetarian hotels in Goa"), you MUST generate a custom plan.
# # 3. **Custom Blueprint**: When generating, "is_custom" must be true. "custom_template_data" must follow this schema:
# #    {{
# #      "objectives": [
# #        {{ "section": "Section Name", "tasks": ["Specific search task 1", "Specific search task 2"] }}
# #      ],
# #      "settings": {{ "depth": "intermediate" }}
# #    }}

# # ### OUTPUT ONLY JSON:
# # {{
# #   "clarification_needed": false,
# #   "domain": "travel",
# #   "templates": ["list_of_matches"],
# #   "target": "string",
# #   "is_custom": boolean,
# #   "custom_template_data": object_or_null,
# #   "confirmation_message": "string"
# # }}
# # """
# #     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"Query: {user_query}")
# #     parsed = sanitize_json_string(raw)

# #     if not isinstance(parsed, dict) or parsed.get("clarification_needed"):
# #         return state, "clarification_needed"

# #     # LOGIC: Load from file OR use the LLM's custom generation
# #     if parsed.get("is_custom"):
# #         research_brief = parsed["custom_template_data"]
# #         print(f"✨ Created Dynamic Custom Template for: {parsed['target']}")
# #     else:
# #         research_brief = loader.load_from_domain(
# #             domain=parsed.get("domain"),
# #             template=parsed.get("templates")[0],
# #             target=parsed.get("target")
# #         )

# #     state["research_brief"] = research_brief
# #     state["mission_id"] = save_mission_to_db(user_query, parsed["target"], "custom" if parsed["is_custom"] else parsed["templates"][0], research_brief)
    
# #     return state, "research_brief"
# import json
# from datetime import date
# from typing import Dict, Any, List
# from my_llm.ollama_client import chat_with_llm
# from utils.json_sanitizer import sanitize_json_string
# from core.template_parser import ResearchTemplateLoader
# from utils.db_manager import save_mission_to_db 

# ResearchState = Dict[str, Any]

# def scoping_and_clarification(state: ResearchState, depth=0) -> (ResearchState, str):
#     user_query = state.get("user_query", "")
#     loader = ResearchTemplateLoader()
#     domain_map = loader.get_domain_map() 

#     # 1. THE ADVANCED PROMPT
#     # We define the schema and the "No-General" rule strictly here.
#     system_prompt = f"""
# You are the Scoping Intelligence of a Deep Research Agent. 
# Your goal is to map the User Query to a specific Domain and one or more Templates.

# ### AVAILABLE TAXONOMY:
# {json.dumps(domain_map, indent=2)}

# ### STRICT OPERATIONAL RULES:
# 1. **NO LAZY GENERALIZATION**: Do NOT choose the 'general' template if the query contains specific requirements (e.g., 'vegetarian', 'luxury', 'safety').
# 2. **CUSTOM GENERATION**: If the Available Taxonomy does not perfectly match the user's intent, you MUST set "is_custom": true and generate a custom Research Brief.
# 3. **BLUEPRINT FOR CUSTOM**:
#    - Use "custom_template_data" to define sections and tasks.
#    - Use the placeholder '{{target}}' within tasks so it can be dynamically injected later.
#    - Example: "Find pure-veg restaurants in {{target}}".
# 4. Determine the RESEARCH_MODE:
#    - 'fast': Use this for straightforward lookups, simple facts, or when the user wants a quick answer.
#    - 'deep': Use this for complex analysis, market research, or when the user asks for a 'detailed' or 'thorough' report.
# ### OUTPUT JSON SCHEMA:
# {{
#   "clarification_needed": bool,
#   "domain": "string",
#   "target": "string",
#   "templates": ["list", "of", "template_names"],
#   "is_custom": bool,
#   "custom_template_data": {{
#       "objectives": [
#           {{ "section": "Section Name", "tasks": ["task 1", "task 2"] }}
#       ],
#       "settings": {{ "depth": "intermediate" }}
#   }},
#   "confirmation_message": "string"
# }}
# """

#     # 2. CALL LLM
#     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User Request: {user_query}")
#     parsed = sanitize_json_string(raw)

#     # 3. SAFETY & CLARIFICATION CHECK
#     if not isinstance(parsed, dict) or parsed.get("clarification_needed", True):
#         state["scoping_result"] = parsed
#         return state, "clarification_needed"

#     target_entity = parsed.get("target", "Unknown")
#     domain_name = parsed.get("domain", "general")
    
#     # 4. DATA PROCESSING (CUSTOM vs. TEMPLATE)
#     try:
#         if parsed.get("is_custom") and "custom_template_data" in parsed:
#             # OPTION A: Use the LLM's dynamically generated brief
#             research_brief = parsed["custom_template_data"]
#             # Inject the target name into the generated tasks
#             for section in research_brief.get("objectives", []):
#                 section["tasks"] = [t.replace("{target}", target_entity) for t in section["tasks"]]
#             selected_templates = ["dynamic_custom"]
#         else:
#             # OPTION B: Load from existing YAML files (Supports Multi-Template)
#             template_list = parsed.get("templates", ["general"])
#             # Ensure your loader has a method to merge multiple templates
#             research_brief = loader.load_multiple_from_domain(
#                 domain=domain_name,
#                 templates=template_list, 
#                 target=target_entity
#             )
#             selected_templates = template_list

#         # Update State
#         state["scoping_result"] = parsed
#         state["research_brief"] = research_brief
#         state["active_domain"] = domain_name
#         state["selected_templates"] = selected_templates
#         state["research_mode"] = parsed.get("research_mode", "fast") # <--- CRITICAL
#         state["target"] = target_entity # <--- CRITICAL
        
#     except Exception as e:
#         print(f"❌ Scoping Logic Error: {e}")
#         return state, "clarification_needed"

#     # 5. PERSISTENCE (POSTGRES)
#     try:
#         mission_id = save_mission_to_db(
#             user_query=user_query,
#             target=target_entity,
#             template=", ".join(selected_templates),
#             research_brief=research_brief,
#             domain=domain_name
#         )
#         state["mission_id"] = mission_id
#         print(f"💾 Mission {mission_id} saved under domain: {domain_name}")
#     except Exception as db_err:
#         print(f"⚠️ DB Warning: {db_err}")

#     return state, "research_brief"
import json
from typing import Dict, Any, Tuple
from my_llm.ollama_client import chat_with_llm
from utils.json_sanitizer import sanitize_json_string
from nodes.research import run_fast_research, run_deep_research 
# For Deep Mode persistence
import psycopg2

ResearchState = Dict[str, Any]

def scoping_and_clarification(state: ResearchState) -> Tuple[ResearchState, str]:
    user_query = state.get("user_query", "")
    
    system_prompt = """
    You are a Research Router. Analyze the user query and decide between 'fast' and 'deep' mode.
    
    1. FAST MODE: Use for simple lookups, recommendations, or quick facts. 
       - If Fast, generate 3-4 specific search queries (fast_tasks).
    2. DEEP MODE: Use for complex analysis, detailed travel planning, or multi-step research.
       - If Deep, select appropriate templates (e.g., luxury_travel, budget_travel, general).

    Return ONLY JSON:
    {
      "reasoning": "Why you chose this mode",
      "research_mode": "fast" | "deep",
      "target": "The main subject (e.g., Goa)",
      "domain": "travel",
      "templates": ["list_of_templates_if_deep"],
      "fast_tasks": ["query 1", "query 2", "query 3"],
      "clarification_needed": false,
      "clarification_question": ""
    }
    """

    # 1. Call LLM to Route
    raw_response = chat_with_llm(system_prompt=system_prompt, user_prompt=user_query)
    scoping_result = sanitize_json_string(raw_response)
    
    # 2. Update State
    state["research_mode"] = scoping_result.get("research_mode", "fast")
    state["target"] = scoping_result.get("target", "subject")
    state["active_domain"] = scoping_result.get("domain", "general")
    state["scoping_result"] = scoping_result

    # 3. Handle Branching Logic
    if scoping_result.get("clarification_needed"):
        return state, "clarification_needed"

    if state["research_mode"] == "fast":
        # BYPASS: Directly set sub_questions so research node can start immediately
        state["sub_questions"] = scoping_result.get("fast_tasks", [user_query])
        print(f"⚡ Fast Route Selected. Tasks: {len(state['sub_questions'])}")
        return state, "fast_research" # This string must match your graph edge

    else:
        # DEEP ROUTE: Initialize Postgres Mission for persistence
        print(f"🧪 Deep Route Selected. Templates: {scoping_result.get('templates')}")
        mission_id = _create_postgres_mission(state, scoping_result)
        state["mission_id"] = mission_id
        return state, "research_brief"

def _create_postgres_mission(state: ResearchState, scoping: Dict) -> int:
    """Helper to create a persistent mission record for Deep Research."""
    try:
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO research_missions (query, domain, status) VALUES (%s, %s, 'scoped') RETURNING id",
            (state["user_query"], scoping.get("domain", "general"))
        )
        m_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return m_id
    except Exception as e:
        print(f"❌ DB Mission Creation Failed: {e}")
        return 0