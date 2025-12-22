# # # # nodes/research_brief.py

# # from datetime import datetime
# # from typing import Dict, Any
# # import json

# # from my_llm.ollama_client import ollama_chat
# # from utils.json_sanitizer import sanitize_json_string
# # from core.template_parser import ResearchTemplateLoader # <-- 1. Import your loader

# # ResearchState = Dict[str, Any]

# # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# #     # 2. Get the template and target identified in scoping
# #     scoping_result = state.get("scoping_result", {})
# #     user_query = state.get("user_query", "")
# #     template_name = scoping_result.get("template", "general_research")
# #     target = scoping_result.get("target", "the subject")

# #     # 3. Load the predefined template tasks
# #     loader = ResearchTemplateLoader()
# #     base_plan = loader.load_and_customize(template_name, target)
    
# #     # Extract the tasks from your YAML to show the LLM
# #     standard_tasks = []
# #     for section in base_plan.get('objectives', []):
# #         standard_tasks.extend(section.get('tasks', []))

# #     system_prompt = f"""
# # You are the Research Brief Agent. Your job is to take a BASE TEMPLATE and refine it into a SPECIFIC research plan.

# # BASE TEMPLATE TASKS for {target}:
# # {json.dumps(standard_tasks, indent=2)}

# # Your Goal: 
# # 1. Use the Base Template as your foundation.
# # 2. Add 2-3 custom 'sub_questions' based on the user's specific query.
# # 3. Determine the 'coverage_depth' based on the template's 'depth' setting ({base_plan['settings']['depth']}).

# # Return ONLY valid JSON:
# # {{
# #   "research_question": "<refined main question>",
# #   "sub_questions": ["<task from template>", "<custom task>", ...],
# #   "coverage_depth": "<overview | intermediate | deep>",
# #   "must_cover": ["<priority sources or topics from template>"],
# #   "summary": "<brief summary>"
# # }}
# # """

# #     user_message = f"User Request: {user_query}\nTarget: {target}"

# #     # ---- CALL OLLAMA ----
# #     raw = ollama_chat(system_prompt=system_prompt, user_prompt=user_message)
# #     parsed = sanitize_json_string(raw)

# #     # 4. Merge settings back in (ensures the search engine sees the whitelist/depth)
# #     parsed['settings'] = base_plan.get('settings', {})
    
# #     state["research_brief"] = parsed
# #     print(f"✅ Brief finalized with {len(parsed['sub_questions'])} tasks.")
    
# #     return state, "research"
# # nodes/research_brief.py
# import psycopg2
# import json
# from datetime import datetime
# from typing import Dict, Any
# from my_llm.ollama_client import chat_with_llm
# from utils.json_sanitizer import sanitize_json_string
# from core.template_parser import ResearchTemplateLoader

# ResearchState = Dict[str, Any]

# def build_research_brief(state: ResearchState) -> (ResearchState, str):
#     scoping_result = state.get("scoping_result", {})
#     user_query = state.get("user_query", "")
#     # template_name = scoping_result.get("template", "general_research")
#     # target = scoping_result.get("target", "the subject")
#     # mission_id = state.get("mission_id") # Generated in scoping.py
#     domain = scoping_result.get("domain", "travel") # Default to travel if not found
#     template_name = scoping_result.get("template", "general")
#     target = scoping_result.get("target", "the subject")
#     mission_id = state.get("mission_id")
#     loader = ResearchTemplateLoader()
#     try:
#         # Use the new name and pass the 'domain' argument
#         base_plan = loader.load_from_domain(
#             domain=domain, 
#             template=template_name, 
#             target=target
#         )
#     except Exception as e:
#         print(f"❌ Error loading template: {e}")
#         # Fallback to a general plan if the specific one fails
#         return state, "clarification_needed"
    
#     standard_tasks = []
#     for section in base_plan.get('objectives', []):
#         standard_tasks.extend(section.get('tasks', []))

#     system_prompt =  f"""
# You are the Research Brief Agent. Your job is to  take a BASE TEMPLATE and refine it into a SPECIFIC research plan.

#  BASE TEMPLATE TASKS for {target}:
# {json.dumps(standard_tasks, indent=2)}

# Your Goal: 
# 1. Use the Base Template as your foundation.
# 2. Add 2-3 custom 'sub_questions' based on the user's specific query.
# 3. Determine the 'coverage_depth' based on the template's 'depth' setting ({base_plan['settings']['depth']}).
# Return ONLY valid JSON:
#  {{
#    "research_question": "<refined main question>",
#    "sub_questions": ["<task from template>", "<custom task>", ...],
#    "coverage_depth": "<overview | intermediate | deep>",
#    "must_cover": ["<priority sources or topics from template>"],
#    "summary": "<brief summary>"
# }}
# """

#     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User: {user_query}")
#     parsed = sanitize_json_string(raw)
#     parsed['settings'] = base_plan.get('settings', {})
#     state["research_brief"] = parsed

#     # ---- NEW: PERSIST TASKS TO POSTGRES ----
#     if mission_id:
#         try:
#             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
#             cur = conn.cursor()
            
#             # 1. Update the Mission with the finalized brief
#             cur.execute(
#                 "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
#                 (json.dumps(parsed), mission_id)
#             )
            
#             # 2. Insert individual sub-questions as tasks
#             for task_text in parsed.get("sub_questions", []):
#                 cur.execute(
#                     "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
#                     (mission_id, task_text)
#                 )
            
#             conn.commit()
#             cur.close()
#             conn.close()
#             print(f"✅ Mission {mission_id} updated with {len(parsed['sub_questions'])} tasks in DB.")
#         except Exception as e:
#             print(f"❌ DB Error in Brief Node: {e}")

#     return state, "research"
import psycopg2
import json
from datetime import datetime
from typing import Dict, Any
from my_llm.ollama_client import chat_with_llm
from utils.json_sanitizer import sanitize_json_string
from core.template_parser import ResearchTemplateLoader

ResearchState = Dict[str, Any]

def build_research_brief(state: ResearchState) -> (ResearchState, str):
    scoping_result = state.get("scoping_result", {})
    user_query = state.get("user_query", "")
    
    # 1. Extract Routing Info
    domain = scoping_result.get("domain", "travel")
    template_name = scoping_result.get("template", "general_travel")
    target = scoping_result.get("target", "the subject")
    mission_id = state.get("mission_id")

    # 2. Load the Template (The "Knowledge")
    loader = ResearchTemplateLoader()
    try:
        base_plan = loader.load_from_domain(
            domain=domain, 
            template=template_name, 
            target=target
        )
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return state, "clarification_needed"
    
    # 3. Prepare Tasks for the LLM
    standard_tasks = []
    for section in base_plan.get('objectives', []):
        standard_tasks.extend(section.get('tasks', []))

    # We use the YAML settings to guide the LLM
    template_depth = base_plan.get('settings', {}).get('depth', 'intermediate')

    system_prompt = f"""
You are the Research Brief Agent. Your job is to refine a {domain.upper()} research plan for {target}.

BASE TASKS FROM {template_name.upper()} TEMPLATE:
{json.dumps(standard_tasks, indent=2)}

Your Goal: 
1. Use the Base Tasks as your foundation.
2. Add 2-3 custom 'sub_questions' based on the user's query: "{user_query}"
3. Output a structured plan.

Return ONLY valid JSON:
{{
   "research_question": "Main research goal",
   "sub_questions": ["task 1", "task 2", ...],
   "coverage_depth": "{template_depth}",
   "must_cover": ["key sources"],
   "summary": "Brief explanation"
}}
"""

    # 4. Generate & Sanitize Brief
    raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User Query: {user_query}")
    parsed = sanitize_json_string(raw)
    
    # Merge YAML settings into the final brief so the search node can see them
    parsed['settings'] = base_plan.get('settings', {})
    parsed['domain'] = domain # Ensure domain is tracked
    
    state["research_brief"] = parsed

    # 5. Persistent Update to Postgres
    if mission_id:
        try:
            conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
            cur = conn.cursor()
            
            # Update mission with full brief AND domain
            cur.execute(
                "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
                (json.dumps(parsed), mission_id)
            )
            
            # Clear old tasks if any (optional) and insert new ones
            for task_text in parsed.get("sub_questions", []):
                cur.execute(
                    "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
                    (mission_id, task_text)
                )
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Mission {mission_id} ({domain}) updated in DB.")
        except Exception as e:
            print(f"❌ DB Error in Brief Node: {e}")
    else:
        print("⚠️ No Mission ID found. Skipping DB persistence.")

    return state, "research"