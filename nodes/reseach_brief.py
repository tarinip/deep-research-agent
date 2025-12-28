# # # # # # # # nodes/research_brief.py

# # # # # # from datetime import datetime
# # # # # # from typing import Dict, Any
# # # # # # import json

# # # # # # from my_llm.ollama_client import ollama_chat
# # # # # # from utils.json_sanitizer import sanitize_json_string
# # # # # # from core.template_parser import ResearchTemplateLoader # <-- 1. Import your loader

# # # # # # ResearchState = Dict[str, Any]

# # # # # # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# # # # # #     # 2. Get the template and target identified in scoping
# # # # # #     scoping_result = state.get("scoping_result", {})
# # # # # #     user_query = state.get("user_query", "")
# # # # # #     template_name = scoping_result.get("template", "general_research")
# # # # # #     target = scoping_result.get("target", "the subject")

# # # # # #     # 3. Load the predefined template tasks
# # # # # #     loader = ResearchTemplateLoader()
# # # # # #     base_plan = loader.load_and_customize(template_name, target)
    
# # # # # #     # Extract the tasks from your YAML to show the LLM
# # # # # #     standard_tasks = []
# # # # # #     for section in base_plan.get('objectives', []):
# # # # # #         standard_tasks.extend(section.get('tasks', []))

# # # # # #     system_prompt = f"""
# # # # # # You are the Research Brief Agent. Your job is to take a BASE TEMPLATE and refine it into a SPECIFIC research plan.

# # # # # # BASE TEMPLATE TASKS for {target}:
# # # # # # {json.dumps(standard_tasks, indent=2)}

# # # # # # Your Goal: 
# # # # # # 1. Use the Base Template as your foundation.
# # # # # # 2. Add 2-3 custom 'sub_questions' based on the user's specific query.
# # # # # # 3. Determine the 'coverage_depth' based on the template's 'depth' setting ({base_plan['settings']['depth']}).

# # # # # # Return ONLY valid JSON:
# # # # # # {{
# # # # # #   "research_question": "<refined main question>",
# # # # # #   "sub_questions": ["<task from template>", "<custom task>", ...],
# # # # # #   "coverage_depth": "<overview | intermediate | deep>",
# # # # # #   "must_cover": ["<priority sources or topics from template>"],
# # # # # #   "summary": "<brief summary>"
# # # # # # }}
# # # # # # """

# # # # # #     user_message = f"User Request: {user_query}\nTarget: {target}"

# # # # # #     # ---- CALL OLLAMA ----
# # # # # #     raw = ollama_chat(system_prompt=system_prompt, user_prompt=user_message)
# # # # # #     parsed = sanitize_json_string(raw)

# # # # # #     # 4. Merge settings back in (ensures the search engine sees the whitelist/depth)
# # # # # #     parsed['settings'] = base_plan.get('settings', {})
    
# # # # # #     state["research_brief"] = parsed
# # # # # #     print(f"✅ Brief finalized with {len(parsed['sub_questions'])} tasks.")
    
# # # # # #     return state, "research"
# # # # # # nodes/research_brief.py
# # # # # import psycopg2
# # # # # import json
# # # # # from datetime import datetime
# # # # # from typing import Dict, Any
# # # # # from my_llm.ollama_client import chat_with_llm
# # # # # from utils.json_sanitizer import sanitize_json_string
# # # # # from core.template_parser import ResearchTemplateLoader

# # # # # ResearchState = Dict[str, Any]

# # # # # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# # # # #     scoping_result = state.get("scoping_result", {})
# # # # #     user_query = state.get("user_query", "")
# # # # #     # template_name = scoping_result.get("template", "general_research")
# # # # #     # target = scoping_result.get("target", "the subject")
# # # # #     # mission_id = state.get("mission_id") # Generated in scoping.py
# # # # #     domain = scoping_result.get("domain", "travel") # Default to travel if not found
# # # # #     template_name = scoping_result.get("template", "general")
# # # # #     target = scoping_result.get("target", "the subject")
# # # # #     mission_id = state.get("mission_id")
# # # # #     loader = ResearchTemplateLoader()
# # # # #     try:
# # # # #         # Use the new name and pass the 'domain' argument
# # # # #         base_plan = loader.load_from_domain(
# # # # #             domain=domain, 
# # # # #             template=template_name, 
# # # # #             target=target
# # # # #         )
# # # # #     except Exception as e:
# # # # #         print(f"❌ Error loading template: {e}")
# # # # #         # Fallback to a general plan if the specific one fails
# # # # #         return state, "clarification_needed"
    
# # # # #     standard_tasks = []
# # # # #     for section in base_plan.get('objectives', []):
# # # # #         standard_tasks.extend(section.get('tasks', []))

# # # # #     system_prompt =  f"""
# # # # # You are the Research Brief Agent. Your job is to  take a BASE TEMPLATE and refine it into a SPECIFIC research plan.

# # # # #  BASE TEMPLATE TASKS for {target}:
# # # # # {json.dumps(standard_tasks, indent=2)}

# # # # # Your Goal: 
# # # # # 1. Use the Base Template as your foundation.
# # # # # 2. Add 2-3 custom 'sub_questions' based on the user's specific query.
# # # # # 3. Determine the 'coverage_depth' based on the template's 'depth' setting ({base_plan['settings']['depth']}).
# # # # # Return ONLY valid JSON:
# # # # #  {{
# # # # #    "research_question": "<refined main question>",
# # # # #    "sub_questions": ["<task from template>", "<custom task>", ...],
# # # # #    "coverage_depth": "<overview | intermediate | deep>",
# # # # #    "must_cover": ["<priority sources or topics from template>"],
# # # # #    "summary": "<brief summary>"
# # # # # }}
# # # # # """

# # # # #     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User: {user_query}")
# # # # #     parsed = sanitize_json_string(raw)
# # # # #     parsed['settings'] = base_plan.get('settings', {})
# # # # #     state["research_brief"] = parsed

# # # # #     # ---- NEW: PERSIST TASKS TO POSTGRES ----
# # # # #     if mission_id:
# # # # #         try:
# # # # #             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # # # #             cur = conn.cursor()
            
# # # # #             # 1. Update the Mission with the finalized brief
# # # # #             cur.execute(
# # # # #                 "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
# # # # #                 (json.dumps(parsed), mission_id)
# # # # #             )
            
# # # # #             # 2. Insert individual sub-questions as tasks
# # # # #             for task_text in parsed.get("sub_questions", []):
# # # # #                 cur.execute(
# # # # #                     "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
# # # # #                     (mission_id, task_text)
# # # # #                 )
            
# # # # #             conn.commit()
# # # # #             cur.close()
# # # # #             conn.close()
# # # # #             print(f"✅ Mission {mission_id} updated with {len(parsed['sub_questions'])} tasks in DB.")
# # # # #         except Exception as e:
# # # # #             print(f"❌ DB Error in Brief Node: {e}")

# # # # #     return state, "research"
# # # # import psycopg2
# # # # import json
# # # # from datetime import datetime
# # # # from typing import Dict, Any
# # # # from my_llm.ollama_client import chat_with_llm
# # # # from utils.json_sanitizer import sanitize_json_string
# # # # from core.template_parser import ResearchTemplateLoader

# # # # ResearchState = Dict[str, Any]

# # # # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# # # #     scoping_result = state.get("scoping_result", {})
# # # #     user_query = state.get("user_query", "")
    
# # # #     # 1. Extract Routing Info
# # # #     domain = scoping_result.get("domain", "travel")
# # # #     template_name = scoping_result.get("template", "general_travel")
# # # #     target = scoping_result.get("target", "the subject")
# # # #     mission_id = state.get("mission_id")

# # # #     # 2. Load the Template (The "Knowledge")
# # # #     loader = ResearchTemplateLoader()
# # # #     try:
# # # #         base_plan = loader.load_from_domain(
# # # #             domain=domain, 
# # # #             template=template_name, 
# # # #             target=target
# # # #         )
# # # #     except Exception as e:
# # # #         print(f"❌ Error loading template: {e}")
# # # #         return state, "clarification_needed"
    
# # # #     # 3. Prepare Tasks for the LLM
# # # #     standard_tasks = []
# # # #     for section in base_plan.get('objectives', []):
# # # #         standard_tasks.extend(section.get('tasks', []))

# # # #     # We use the YAML settings to guide the LLM
# # # #     template_depth = base_plan.get('settings', {}).get('depth', 'intermediate')

# # # #     system_prompt = f"""
# # # # You are the Research Brief Agent. Your job is to refine a {domain.upper()} research plan for {target}.

# # # # BASE TASKS FROM {template_name.upper()} TEMPLATE:
# # # # {json.dumps(standard_tasks, indent=2)}

# # # # Your Goal: 
# # # # 1. Use the Base Tasks as your foundation.
# # # # 2. Add 2-3 custom 'sub_questions' based on the user's query: "{user_query}"
# # # # 3. Output a structured plan.

# # # # Return ONLY valid JSON:
# # # # {{
# # # #    "research_question": "Main research goal",
# # # #    "sub_questions": ["task 1", "task 2", ...],
# # # #    "coverage_depth": "{template_depth}",
# # # #    "must_cover": ["key sources"],
# # # #    "summary": "Brief explanation"
# # # # }}
# # # # """

# # # #     # 4. Generate & Sanitize Brief
# # # #     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User Query: {user_query}")
# # # #     parsed = sanitize_json_string(raw)
    
# # # #     # Merge YAML settings into the final brief so the search node can see them
# # # #     parsed['settings'] = base_plan.get('settings', {})
# # # #     parsed['domain'] = domain # Ensure domain is tracked
    
# # # #     state["research_brief"] = parsed

# # # #     # 5. Persistent Update to Postgres
# # # #     if mission_id:
# # # #         try:
# # # #             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # # #             cur = conn.cursor()
            
# # # #             # Update mission with full brief AND domain
# # # #             cur.execute(
# # # #                 "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
# # # #                 (json.dumps(parsed), mission_id)
# # # #             )
            
# # # #             # Clear old tasks if any (optional) and insert new ones
# # # #             for task_text in parsed.get("sub_questions", []):
# # # #                 cur.execute(
# # # #                     "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
# # # #                     (mission_id, task_text)
# # # #                 )
            
# # # #             conn.commit()
# # # #             cur.close()
# # # #             conn.close()
# # # #             print(f"✅ Mission {mission_id} ({domain}) updated in DB.")
# # # #         except Exception as e:
# # # #             print(f"❌ DB Error in Brief Node: {e}")
# # # #     else:
# # # #         print("⚠️ No Mission ID found. Skipping DB persistence.")

# # # #     return state, "research"
# # # import psycopg2
# # # import json
# # # from datetime import datetime
# # # from typing import Dict, Any
# # # from my_llm.ollama_client import chat_with_llm
# # # from utils.json_sanitizer import sanitize_json_string
# # # from core.template_parser import ResearchTemplateLoader

# # # ResearchState = Dict[str, Any]

# # # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# # #     scoping_result = state.get("scoping_result", {})
# # #     user_query = state.get("user_query", "")
    
# # #     # 1. Extract Multi-Template Routing Info
# # #     domain = scoping_result.get("domain", "travel")
# # #     # Change: We now look for 'templates' (list) instead of 'template' (string)
# # #     templates = scoping_result.get("templates", ["general_travel"]) 
# # #     target = scoping_result.get("target", "the subject")
# # #     mission_id = state.get("mission_id")

# # #     # 2. Load and Merge Templates
# # #     loader = ResearchTemplateLoader()
# # #     try:
# # #         # Use the NEW multi-loader method we discussed for template_parser.py
# # #         base_plan = loader.load_multiple_from_domain(
# # #             domain=domain, 
# # #             templates=templates, 
# # #             target=target
# # #         )
# # #     except Exception as e:
# # #         print(f"❌ Error merging templates {templates}: {e}")
# # #         return state, "clarification_needed"
    
# # #     # 3. Prepare Combined Tasks for the LLM
# # #     standard_tasks = []
# # #     for section in base_plan.get('objectives', []):
# # #         standard_tasks.extend(section.get('tasks', []))

# # #     # Determine depth (usually the deepest setting among selected templates)
# # #     template_depth = base_plan.get('settings', {}).get('depth', 'intermediate')

# # #     system_prompt = f"""
# # # You are the Research Brief Agent. Your job is to refine a {domain.upper()} research plan for {target}.
# # # You are synthesizing instructions from multiple specialized tracks: {", ".join(templates)}.

# # # BASE TASKS FROM MERGED TEMPLATES:
# # # {json.dumps(standard_tasks, indent=2)}

# # # Your Goal: 
# # # 1. Use the Base Tasks as your core foundation.
# # # 2. Add 2-3 custom 'sub_questions' that specifically address the user's unique request: "{user_query}"
# # # 3. Ensure the final plan feels cohesive and covers all aspects mentioned in the templates.

# # # Return ONLY valid JSON:
# # # {{
# # #    "research_question": "Main research goal",
# # #    "sub_questions": ["task 1", "task 2", ...],
# # #    "coverage_depth": "{template_depth}",
# # #    "must_cover": ["key sources or critical entities"],
# # #    "summary": "Brief explanation of how these templates satisfy the user's query"
# # # }}
# # # """

# # #     # 4. Generate & Sanitize Brief
# # #     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User Query: {user_query}")
# # #     parsed = sanitize_json_string(raw)
    
# # #     # Merge YAML settings into the final brief so the search node can see them
# # #     parsed['settings'] = base_plan.get('settings', {})
# # #     parsed['domain'] = domain 
# # #     parsed['active_templates'] = templates # Track which templates were used
    
# # #     state["research_brief"] = parsed

# # #     # 5. Persistent Update to Postgres
# # #     if mission_id:
# # #         try:
# # #             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # #             cur = conn.cursor()
            
# # #             # Update mission with full brief (which now contains the combined strategy)
# # #             cur.execute(
# # #                 "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
# # #                 (json.dumps(parsed), mission_id)
# # #             )
            
# # #             # Insert individual sub-questions as tasks for the researcher to pick up
# # #             for task_text in parsed.get("sub_questions", []):
# # #                 cur.execute(
# # #                     "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
# # #                     (mission_id, task_text)
# # #                 )
            
# # #             conn.commit()
# # #             cur.close()
# # #             conn.close()
# # #             print(f"✅ Mission {mission_id} ({domain}) updated in DB with merged templates.")
# # #         except Exception as e:
# # #             print(f"❌ DB Error in Brief Node: {e}")
# # #     else:
# # #         print("⚠️ No Mission ID found. Skipping DB persistence.")

# # #     return state, "research"
# # # # # # # nodes/research_brief.py

# # # # # from datetime import datetime
# # # # # from typing import Dict, Any
# # # # # import json

# # # # # from my_llm.ollama_client import ollama_chat
# # # # # from utils.json_sanitizer import sanitize_json_string
# # # # # from core.template_parser import ResearchTemplateLoader # <-- 1. Import your loader

# # # # # ResearchState = Dict[str, Any]

# # # # # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# # # # #     # 2. Get the template and target identified in scoping
# # # # #     scoping_result = state.get("scoping_result", {})
# # # # #     user_query = state.get("user_query", "")
# # # # #     template_name = scoping_result.get("template", "general_research")
# # # # #     target = scoping_result.get("target", "the subject")

# # # # #     # 3. Load the predefined template tasks
# # # # #     loader = ResearchTemplateLoader()
# # # # #     base_plan = loader.load_and_customize(template_name, target)
    
# # # # #     # Extract the tasks from your YAML to show the LLM
# # # # #     standard_tasks = []
# # # # #     for section in base_plan.get('objectives', []):
# # # # #         standard_tasks.extend(section.get('tasks', []))

# # # # #     system_prompt = f"""
# # # # # You are the Research Brief Agent. Your job is to take a BASE TEMPLATE and refine it into a SPECIFIC research plan.

# # # # # BASE TEMPLATE TASKS for {target}:
# # # # # {json.dumps(standard_tasks, indent=2)}

# # # # # Your Goal: 
# # # # # 1. Use the Base Template as your foundation.
# # # # # 2. Add 2-3 custom 'sub_questions' based on the user's specific query.
# # # # # 3. Determine the 'coverage_depth' based on the template's 'depth' setting ({base_plan['settings']['depth']}).

# # # # # Return ONLY valid JSON:
# # # # # {{
# # # # #   "research_question": "<refined main question>",
# # # # #   "sub_questions": ["<task from template>", "<custom task>", ...],
# # # # #   "coverage_depth": "<overview | intermediate | deep>",
# # # # #   "must_cover": ["<priority sources or topics from template>"],
# # # # #   "summary": "<brief summary>"
# # # # # }}
# # # # # """

# # # # #     user_message = f"User Request: {user_query}\nTarget: {target}"

# # # # #     # ---- CALL OLLAMA ----
# # # # #     raw = ollama_chat(system_prompt=system_prompt, user_prompt=user_message)
# # # # #     parsed = sanitize_json_string(raw)

# # # # #     # 4. Merge settings back in (ensures the search engine sees the whitelist/depth)
# # # # #     parsed['settings'] = base_plan.get('settings', {})
    
# # # # #     state["research_brief"] = parsed
# # # # #     print(f"✅ Brief finalized with {len(parsed['sub_questions'])} tasks.")
    
# # # # #     return state, "research"
# # # # # nodes/research_brief.py
# # # # import psycopg2
# # # # import json
# # # # from datetime import datetime
# # # # from typing import Dict, Any
# # # # from my_llm.ollama_client import chat_with_llm
# # # # from utils.json_sanitizer import sanitize_json_string
# # # # from core.template_parser import ResearchTemplateLoader

# # # # ResearchState = Dict[str, Any]

# # # # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# # # #     scoping_result = state.get("scoping_result", {})
# # # #     user_query = state.get("user_query", "")
# # # #     # template_name = scoping_result.get("template", "general_research")
# # # #     # target = scoping_result.get("target", "the subject")
# # # #     # mission_id = state.get("mission_id") # Generated in scoping.py
# # # #     domain = scoping_result.get("domain", "travel") # Default to travel if not found
# # # #     template_name = scoping_result.get("template", "general")
# # # #     target = scoping_result.get("target", "the subject")
# # # #     mission_id = state.get("mission_id")
# # # #     loader = ResearchTemplateLoader()
# # # #     try:
# # # #         # Use the new name and pass the 'domain' argument
# # # #         base_plan = loader.load_from_domain(
# # # #             domain=domain, 
# # # #             template=template_name, 
# # # #             target=target
# # # #         )
# # # #     except Exception as e:
# # # #         print(f"❌ Error loading template: {e}")
# # # #         # Fallback to a general plan if the specific one fails
# # # #         return state, "clarification_needed"
    
# # # #     standard_tasks = []
# # # #     for section in base_plan.get('objectives', []):
# # # #         standard_tasks.extend(section.get('tasks', []))

# # # #     system_prompt =  f"""
# # # # You are the Research Brief Agent. Your job is to  take a BASE TEMPLATE and refine it into a SPECIFIC research plan.

# # # #  BASE TEMPLATE TASKS for {target}:
# # # # {json.dumps(standard_tasks, indent=2)}

# # # # Your Goal: 
# # # # 1. Use the Base Template as your foundation.
# # # # 2. Add 2-3 custom 'sub_questions' based on the user's specific query.
# # # # 3. Determine the 'coverage_depth' based on the template's 'depth' setting ({base_plan['settings']['depth']}).
# # # # Return ONLY valid JSON:
# # # #  {{
# # # #    "research_question": "<refined main question>",
# # # #    "sub_questions": ["<task from template>", "<custom task>", ...],
# # # #    "coverage_depth": "<overview | intermediate | deep>",
# # # #    "must_cover": ["<priority sources or topics from template>"],
# # # #    "summary": "<brief summary>"
# # # # }}
# # # # """

# # # #     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User: {user_query}")
# # # #     parsed = sanitize_json_string(raw)
# # # #     parsed['settings'] = base_plan.get('settings', {})
# # # #     state["research_brief"] = parsed

# # # #     # ---- NEW: PERSIST TASKS TO POSTGRES ----
# # # #     if mission_id:
# # # #         try:
# # # #             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # # #             cur = conn.cursor()
            
# # # #             # 1. Update the Mission with the finalized brief
# # # #             cur.execute(
# # # #                 "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
# # # #                 (json.dumps(parsed), mission_id)
# # # #             )
            
# # # #             # 2. Insert individual sub-questions as tasks
# # # #             for task_text in parsed.get("sub_questions", []):
# # # #                 cur.execute(
# # # #                     "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
# # # #                     (mission_id, task_text)
# # # #                 )
            
# # # #             conn.commit()
# # # #             cur.close()
# # # #             conn.close()
# # # #             print(f"✅ Mission {mission_id} updated with {len(parsed['sub_questions'])} tasks in DB.")
# # # #         except Exception as e:
# # # #             print(f"❌ DB Error in Brief Node: {e}")

# # # #     return state, "research"
# # # import psycopg2
# # # import json
# # # from datetime import datetime
# # # from typing import Dict, Any
# # # from my_llm.ollama_client import chat_with_llm
# # # from utils.json_sanitizer import sanitize_json_string
# # # from core.template_parser import ResearchTemplateLoader

# # # ResearchState = Dict[str, Any]

# # # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# # #     scoping_result = state.get("scoping_result", {})
# # #     user_query = state.get("user_query", "")
    
# # #     # 1. Extract Routing Info
# # #     domain = scoping_result.get("domain", "travel")
# # #     template_name = scoping_result.get("template", "general_travel")
# # #     target = scoping_result.get("target", "the subject")
# # #     mission_id = state.get("mission_id")

# # #     # 2. Load the Template (The "Knowledge")
# # #     loader = ResearchTemplateLoader()
# # #     try:
# # #         base_plan = loader.load_from_domain(
# # #             domain=domain, 
# # #             template=template_name, 
# # #             target=target
# # #         )
# # #     except Exception as e:
# # #         print(f"❌ Error loading template: {e}")
# # #         return state, "clarification_needed"
    
# # #     # 3. Prepare Tasks for the LLM
# # #     standard_tasks = []
# # #     for section in base_plan.get('objectives', []):
# # #         standard_tasks.extend(section.get('tasks', []))

# # #     # We use the YAML settings to guide the LLM
# # #     template_depth = base_plan.get('settings', {}).get('depth', 'intermediate')

# # #     system_prompt = f"""
# # # You are the Research Brief Agent. Your job is to refine a {domain.upper()} research plan for {target}.

# # # BASE TASKS FROM {template_name.upper()} TEMPLATE:
# # # {json.dumps(standard_tasks, indent=2)}

# # # Your Goal: 
# # # 1. Use the Base Tasks as your foundation.
# # # 2. Add 2-3 custom 'sub_questions' based on the user's query: "{user_query}"
# # # 3. Output a structured plan.

# # # Return ONLY valid JSON:
# # # {{
# # #    "research_question": "Main research goal",
# # #    "sub_questions": ["task 1", "task 2", ...],
# # #    "coverage_depth": "{template_depth}",
# # #    "must_cover": ["key sources"],
# # #    "summary": "Brief explanation"
# # # }}
# # # """

# # #     # 4. Generate & Sanitize Brief
# # #     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User Query: {user_query}")
# # #     parsed = sanitize_json_string(raw)
    
# # #     # Merge YAML settings into the final brief so the search node can see them
# # #     parsed['settings'] = base_plan.get('settings', {})
# # #     parsed['domain'] = domain # Ensure domain is tracked
    
# # #     state["research_brief"] = parsed

# # #     # 5. Persistent Update to Postgres
# # #     if mission_id:
# # #         try:
# # #             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # #             cur = conn.cursor()
            
# # #             # Update mission with full brief AND domain
# # #             cur.execute(
# # #                 "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
# # #                 (json.dumps(parsed), mission_id)
# # #             )
            
# # #             # Clear old tasks if any (optional) and insert new ones
# # #             for task_text in parsed.get("sub_questions", []):
# # #                 cur.execute(
# # #                     "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
# # #                     (mission_id, task_text)
# # #                 )
            
# # #             conn.commit()
# # #             cur.close()
# # #             conn.close()
# # #             print(f"✅ Mission {mission_id} ({domain}) updated in DB.")
# # #         except Exception as e:
# # #             print(f"❌ DB Error in Brief Node: {e}")
# # #     else:
# # #         print("⚠️ No Mission ID found. Skipping DB persistence.")

# # #     return state, "research"
# # import psycopg2
# # import json
# # from datetime import datetime
# # from typing import Dict, Any
# # from my_llm.ollama_client import chat_with_llm
# # from utils.json_sanitizer import sanitize_json_string
# # from core.template_parser import ResearchTemplateLoader

# # ResearchState = Dict[str, Any]

# # def build_research_brief(state: ResearchState) -> (ResearchState, str):
# #     scoping_result = state.get("scoping_result", {})
# #     user_query = state.get("user_query", "")
    
# #     # 1. Extract Multi-Template Routing Info
# #     domain = scoping_result.get("domain", "travel")
# #     # Change: We now look for 'templates' (list) instead of 'template' (string)
# #     templates = scoping_result.get("templates", ["general_travel"]) 
# #     target = scoping_result.get("target", "the subject")
# #     mission_id = state.get("mission_id")

# #     # 2. Load and Merge Templates
# #     loader = ResearchTemplateLoader()
# #     try:
# #         # Use the NEW multi-loader method we discussed for template_parser.py
# #         base_plan = loader.load_multiple_from_domain(
# #             domain=domain, 
# #             templates=templates, 
# #             target=target
# #         )
# #     except Exception as e:
# #         print(f"❌ Error merging templates {templates}: {e}")
# #         return state, "clarification_needed"
    
# #     # 3. Prepare Combined Tasks for the LLM
# #     standard_tasks = []
# #     for section in base_plan.get('objectives', []):
# #         standard_tasks.extend(section.get('tasks', []))

# #     # Determine depth (usually the deepest setting among selected templates)
# #     template_depth = base_plan.get('settings', {}).get('depth', 'intermediate')

# #     system_prompt = f"""
# # You are the Research Brief Agent. Your job is to refine a {domain.upper()} research plan for {target}.
# # You are synthesizing instructions from multiple specialized tracks: {", ".join(templates)}.

# # BASE TASKS FROM MERGED TEMPLATES:
# # {json.dumps(standard_tasks, indent=2)}

# # Your Goal: 
# # 1. Use the Base Tasks as your core foundation.
# # 2. Add 2-3 custom 'sub_questions' that specifically address the user's unique request: "{user_query}"
# # 3. Ensure the final plan feels cohesive and covers all aspects mentioned in the templates.

# # Return ONLY valid JSON:
# # {{
# #    "research_question": "Main research goal",
# #    "sub_questions": ["task 1", "task 2", ...],
# #    "coverage_depth": "{template_depth}",
# #    "must_cover": ["key sources or critical entities"],
# #    "summary": "Brief explanation of how these templates satisfy the user's query"
# # }}
# # """

# #     # 4. Generate & Sanitize Brief
# #     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=f"User Query: {user_query}")
# #     parsed = sanitize_json_string(raw)
    
# #     # Merge YAML settings into the final brief so the search node can see them
# #     parsed['settings'] = base_plan.get('settings', {})
# #     parsed['domain'] = domain 
# #     parsed['active_templates'] = templates # Track which templates were used
    
# #     state["research_brief"] = parsed

# #     # 5. Persistent Update to Postgres
# #     if mission_id:
# #         try:
# #             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# #             cur = conn.cursor()
            
# #             # Update mission with full brief (which now contains the combined strategy)
# #             cur.execute(
# #                 "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
# #                 (json.dumps(parsed), mission_id)
# #             )
            
# #             # Insert individual sub-questions as tasks for the researcher to pick up
# #             for task_text in parsed.get("sub_questions", []):
# #                 cur.execute(
# #                     "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
# #                     (mission_id, task_text)
# #                 )
            
# #             conn.commit()
# #             cur.close()
# #             conn.close()
# #             print(f"✅ Mission {mission_id} ({domain}) updated in DB with merged templates.")
# #         except Exception as e:
# #             print(f"❌ DB Error in Brief Node: {e}")
# #     else:
# #         print("⚠️ No Mission ID found. Skipping DB persistence.")

# #     return state, "research"
# import psycopg2
# import json
# from typing import Dict, Any
# from my_llm.ollama_client import chat_with_llm
# from utils.json_sanitizer import sanitize_json_string
# from core.template_parser import ResearchTemplateLoader

# ResearchState = Dict[str, Any]

# def build_research_brief(state: ResearchState) -> (ResearchState, str):
#     # 1. Pull data from the exact keys set in scoping.py
#     scoping_result = state.get("scoping_result", {})
#     user_query = state.get("user_query", "")
#     mission_id = state.get("mission_id")
    
#     # FIX: scoping.py uses 'templates' (plural)
#     # We pull from scoping_result specifically
#     domain = state.get("active_domain", "travel") 
#     selected_templates = scoping_result.get("templates", ["general_travel"]) 
#     target = scoping_result.get("target", state.get("target", "the subject"))

#     print(f"🧪 Briefing Node: Loading tracks {selected_templates} for {target}")

#     loader = ResearchTemplateLoader()
#     try:
#         # Load the YAML content based on the templates chosen in scoping
#         base_plan = loader.load_multiple_from_domain(
#             domain=domain, 
#             templates=selected_templates, 
#             target=target
#         )
#     except Exception as e:
#         print(f"❌ Template Load Error: {e}")
#         return state, "clarification_needed"
    
#     # 2. Extract tasks from the loaded YAML
#     standard_tasks = []
#     for section in base_plan.get('objectives', []):
#         standard_tasks.extend(section.get('tasks', []))

#     # 3. Ask LLM to refine these into a JSON list
#     system_prompt = f"Refine these {domain} tasks for {target}. Return JSON with 'sub_questions' list."
#     raw = chat_with_llm(system_prompt=system_prompt, user_prompt=user_query)
#     parsed = sanitize_json_string(raw)
    
#     # 4. CRITICAL: Handover to Research Node
#     # This prevents the "0 tasks" error
#     state["research_brief"] = parsed
#     state["sub_questions"] = parsed.get("sub_questions", []) 
    
#     print(f"✅ Brief finalized with {len(state['sub_questions'])} tasks.")
    
#     # 5. DB Persistence
#     if mission_id:
#         _persist_deep_brief(mission_id, parsed)

#     return state, "research"

# def _persist_deep_brief(mission_id: int, brief: Dict):
#     """Helper to save the detailed plan to Postgres."""
#     try:
#         conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
#         cur = conn.cursor()
#         cur.execute(
#             "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
#             (json.dumps(brief), mission_id)
#         )
#         for task_text in brief.get("sub_questions", []):
#             cur.execute(
#                 "INSERT INTO research_tasks (mission_id, question) VALUES (%s, %s)",
#                 (mission_id, task_text)
#             )
#         conn.commit()
#         cur.close()
#         conn.close()
#     except Exception as e:
#         print(f"❌ DB Error: {e}")
import psycopg2
import json
from typing import Dict, Any, Tuple
from my_llm.ollama_client import chat_with_llm
from utils.json_sanitizer import sanitize_json_string
from core.template_parser import ResearchTemplateLoader
from datetime import datetime
ResearchState = Dict[str, Any]

def build_research_brief(state: ResearchState) -> Tuple[ResearchState, str]:
    # 1. Pull data from state
    print(state)
    scoping_result = state.get("scoping_result", {})
    user_query = state.get("user_query", "")
    mission_id = state.get("mission_id")
    
    current_date = datetime.now().strftime("%B %d, %Y")
    # FIX: Explicitly pull the list of templates from scoping_result
    domain = state.get("active_domain", "travel") 
    selected_templates = scoping_result.get("templates", ["general_travel"]) 
    target = scoping_result.get("target", "the subject")

    print(f"🧪 Briefing Node: Merging {len(selected_templates)} tracks: {selected_templates}")

    loader = ResearchTemplateLoader()
    try:
        # Load and combine all objectives from luxury, booking, and identity templates
        base_plan = loader.load_multiple_from_domain(
            domain=domain, 
            templates=selected_templates, 
            target=target
        )
    except Exception as e:
        print(f"❌ Template Load Error: {e}")
        return state, "clarification_needed"
    
    # 2. Collect all tasks from the merged plan
    standard_tasks = []
    for section in base_plan.get('objectives', []):
        standard_tasks.extend(section.get('tasks', []))

    # 3. LLM Refinement
    system_prompt = f"""
    Refine these {domain} objectives for {target}. 
    User Query: {user_query}
    CURRENT DATE: {current_date}
    Merged Templates: {selected_templates}
    Objectives: {json.dumps(standard_tasks)}
    
    Return ONLY valid JSON:
    {{
      "research_question": "Main goal",
      "sub_questions": ["task 1", "task 2", ...],
      "summary": "Cohesive plan summary"
    }}
    """
    
    raw = chat_with_llm(system_prompt=system_prompt, user_prompt=user_query)
    parsed = sanitize_json_string(raw)
    
    # 4. Update State (Crucial for the next Research Loop)
    state["research_brief"] = parsed
    state["sub_questions"] = parsed.get("sub_questions", [])
    
    # 5. PERSISTENCE FIX: Convert dict to JSON string for Postgres
    if mission_id:
        try:
            conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
            cur = conn.cursor()
            
            # FIX: Use json.dumps() to avoid "can't adapt type 'dict'" error
            brief_json_string = json.dumps(parsed)
            
            cur.execute(
                "UPDATE research_missions SET research_brief = %s, status = 'briefed' WHERE id = %s",
                (brief_json_string, mission_id)
            )
            
            # Insert individual sub-questions
            for task_text in state["sub_questions"]:
                cur.execute(
                    "INSERT INTO research_tasks (mission_id, question, status) VALUES (%s, %s, 'pending')",
                    (mission_id, task_text)
                )
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Mission {mission_id} updated and tasks inserted.")
        except Exception as e:
            print(f"❌ DB Error in Briefing Node: {e}")

    return state, "research"