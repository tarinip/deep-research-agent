# # # # # # # nodes/synthesis.py

# # # # # # from typing import Dict, Any, List, Optional
# # # # # # import json
# # # # # # from my_llm.ollama_client import ollama_chat # Assumed import for your LLM client
# # # # # # # from utils.json_sanitizer import sanitize_json_string # Not strictly needed here

# # # # # # ResearchState = Dict[str, Any]

# # # # # # def run_synthesis(state: ResearchState) -> ResearchState:
# # # # # #     """
# # # # # #     Analyzes the raw research data against the brief and generates the final report
# # # # # #     using an LLM for synthesis. 

# # # # # # [Image of RAG process diagram]

# # # # # #     """
# # # # # #     print("\n✍️ Running Synthesis Node (Generating Final Report)...")

# # # # # #     # 1. Get all necessary components from the state
# # # # # #     research_brief: Dict[str, Any] = state.get("research_brief", {})
# # # # # #     raw_results: List[Dict] = state.get("raw_research_output", [])
# # # # # #     reflection_log: str = state.get("reflection_log", "No reflection log available.")
    
# # # # # #     # 2. Extract, clean, and format the research data (RAG Context)
# # # # # #     search_context_list = []
    
# # # # # #     for query_data in raw_results:
# # # # # #         # Only process successful queries that returned organic results
# # # # # #         if query_data.get('status') == 'success' and query_data.get('raw_json_result', {}).get('organic_results'):
            
# # # # # #             snippets = []
# # # # # #             # Extract just the title, snippet, and source link for the LLM prompt
# # # # # #             for result in query_data['raw_json_result']['organic_results']:
# # # # # #                 snippets.append({
# # # # # #                     "title": result.get('title'),
# # # # # #                     "snippet": result.get('snippet'),
# # # # # #                     "source": result.get('link')
# # # # # #                 })
            
# # # # # #             search_context_list.append({
# # # # # #                 "query": query_data['query'],
# # # # # #                 "results": snippets
# # # # # #             })
            
# # # # # #     search_context_str = json.dumps(search_context_list, indent=2)


# # # # # #     # 3. LLM Prompt Construction (The Synthesis Task)
# # # # # # #     system_prompt = """
# # # # # # # You are the Final Synthesis Agent. Your task is to use the provided Research Brief 
# # # # # # # and Raw Research Context (gathered from search engines) to write a comprehensive, 
# # # # # # # final report.

# # # # # # # Instructions:
# # # # # # # 1. Adhere strictly to the constraints, format, and depth specified in the Research Brief.
# # # # # # # 2. Use ONLY the information provided in the Raw Research Context to generate the report. Do not use outside knowledge.
# # # # # # # 3. Structure your final output clearly, addressing all 'sub_questions' from the brief.
# # # # # # # 4. If the data is insufficient for a sub-question, clearly state the gap based on the reflection log.
# # # # # # # 5. Your final output should be a plain text report, suitable for immediate viewing.
# # # # # # # """
# # # # # #    report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")
# # # # # #    target = research_brief.get("target", "the subject")

# # # # # #    system_prompt = f"""
# # # # # # You are a Senior Research Analyst writing a "{report_name}" about {target}.

# # # # # # Instructions:
# # # # # # 1. Format: Use clean Markdown (Headers, Bullet points, Bold text).
# # # # # # 2. Traceability: When you state a fact, try to include the source title or link from the context provided.
# # # # # # 3. Structure: 
# # # # # #    - Start with an 'Executive Summary'.
# # # # # #    - Create sections for each sub-question.
# # # # # #    - Conclude with a 'Sources' section listing the unique links found in the context.

# # # # # # Constraint: Use ONLY the provided context. If the data is missing, mark it as 'Information not available'.
# # # # # # """
# # # # # #    user_prompt = f"""
# # # # # # ### RESEARCH BRIEF (The Plan) ###
# # # # # # {json.dumps(research_brief, indent=2)}

# # # # # # ### RAW RESEARCH CONTEXT (The Data) ###
# # # # # # {search_context_str}

# # # # # # ### REFLECTION LOG ###
# # # # # # {reflection_log}

# # # # # # Based on the plan and the context provided, generate the full final report now.
# # # # # # """

# # # # # #     # 4. Call the LLM (Live Integration)
# # # # # #     try:
# # # # # #         # Assuming ollama_chat accepts system and user prompts and returns the text response
# # # # # #         raw_report = ollama_chat(system_prompt=system_prompt, user_prompt=user_prompt)
# # # # # #     except Exception as e:
# # # # # #         # Fallback if the LLM call fails
# # # # # #         raw_report = f"*** Synthesis Failed: Could not generate report. Error: {e} ***\n\nContext Provided:\n{search_context_str}"


# # # # # #     # 5. Update the state with the final result
# # # # # #     state["final_report"] = raw_report
    
# # # # # #     print("\n🎉 Synthesis complete. Final report generated.")
# # # # # #     return state
# # # # # # nodes/synthesis.py

# # # # # from typing import Dict, Any, List, Optional
# # # # # import json
# # # # # from my_llm.ollama_client import ollama_chat # Assumed import for your LLM client

# # # # # ResearchState = Dict[str, Any]

# # # # # def run_synthesis(state: ResearchState) -> ResearchState:
# # # # #     """
# # # # #     Analyzes the raw research data against the brief and generates the final report
# # # # #     using an LLM for synthesis. 
# # # # #     """
# # # # #     print("\n✍️ Running Synthesis Node (Generating Final Report)...")

# # # # #     # 1. Get all necessary components from the state
# # # # #     research_brief: Dict[str, Any] = state.get("research_brief", {})
# # # # #     raw_results: List[Dict] = state.get("raw_research_output", [])
# # # # #     reflection_log: str = state.get("reflection_log", "No reflection log available.")
    
# # # # #     # 2. Extract, clean, and format the research data (RAG Context)
# # # # #     search_context_list = []
    
# # # # #     for query_data in raw_results:
# # # # #         if query_data.get('status') == 'success' and query_data.get('raw_json_result', {}).get('organic_results'):
# # # # #             snippets = []
# # # # #             for result in query_data['raw_json_result']['organic_results']:
# # # # #                 snippets.append({
# # # # #                     "title": result.get('title'),
# # # # #                     "snippet": result.get('snippet'),
# # # # #                     "source": result.get('link')
# # # # #                 })
            
# # # # #             search_context_list.append({
# # # # #                 "query": query_data['query'],
# # # # #                 "results": snippets
# # # # #             })
            
# # # # #     search_context_str = json.dumps(search_context_list, indent=2)

# # # # #     # 3. LLM Prompt Construction (Corrected Indentation Here)
# # # # #     report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")
# # # # #     target = research_brief.get("target", "the subject")

# # # # #     system_prompt = f"""
# # # # # You are a Senior Research Analyst writing a "{report_name}" about {target}.

# # # # # Instructions:
# # # # # 1. Format: Use clean Markdown (Headers, Bullet points, Bold text).
# # # # # 2. Traceability: When you state a fact, try to include the source title or link from the context provided.
# # # # # 3. Structure: 
# # # # #    - Start with an 'Executive Summary'.
# # # # #    - Create sections for each sub-question.
# # # # #    - Conclude with a 'Sources' section listing the unique links found in the context.

# # # # # Constraint: Use ONLY the provided context. If the data is missing, mark it as 'Information not available'.
# # # # # """
# # # # #     user_prompt = f"""
# # # # # ### RESEARCH BRIEF (The Plan) ###
# # # # # {json.dumps(research_brief, indent=2)}

# # # # # ### RAW RESEARCH CONTEXT (The Data) ###
# # # # # {search_context_str}

# # # # # ### REFLECTION LOG ###
# # # # # {reflection_log}

# # # # # Based on the plan and the context provided, generate the full final report now.
# # # # # """

# # # # #     # 4. Call the LLM (Live Integration)
# # # # #     try:
# # # # #         raw_report = ollama_chat(system_prompt=system_prompt, user_prompt=user_prompt)
# # # # #     except Exception as e:
# # # # #         raw_report = f"*** Synthesis Failed: Could not generate report. Error: {e} ***\n\nContext Provided:\n{search_context_str}"

# # # # #     # 5. Update the state with the final result
# # # # #     state["final_report"] = raw_report
    
# # # # #     print("\n🎉 Synthesis complete. Final report generated.")
# # # # #     return state
# # # # # nodes/synthesis.py
# # # # import psycopg2
# # # # import json
# # # # from typing import Dict, Any
# # # # from my_llm.ollama_client import chat_with_llm

# # # # ResearchState = Dict[str, Any]

# # # # def run_synthesis(state: ResearchState) -> ResearchState:
# # # #     print("\n✍️ Running Synthesis Node (Querying Postgres Memory)...")

# # # #     mission_id = state.get("mission_id")
# # # #     research_brief = state.get("research_brief", {})
# # # #     target = research_brief.get("target", "the subject")
# # # #     report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")

# # # #     # 1. Pull ALL findings from Postgres for this mission
# # # #     try:
# # # #         conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # # #         cur = conn.cursor()
        
# # # #         cur.execute(
# # # #             "SELECT topic, content, source_url FROM research_nodes WHERE mission_id = %s",
# # # #             (mission_id,)
# # # #         )
# # # #         db_rows = cur.fetchall()
        
# # # #         # Format the data for the LLM
# # # #         context_blocks = []
# # # #         for row in db_rows:
# # # #             context_blocks.append(f"TOPIC: {row[0]}\nFINDING: {row[1]}\nSOURCE: {row[2]}\n---")
        
# # # #         full_context = "\n".join(context_blocks)
# # # #         cur.close()
# # # #         conn.close()
# # # #     except Exception as e:
# # # #         print(f"❌ DB Error in Synthesis: {e}")
# # # #         full_context = "No data found in database."

# # # #     # 2. Construct the Prompt
# # # #     system_prompt = f"""
# # # # You are a Senior Research Analyst writing the '{report_name}' for {target}.
# # # # Your goal is to synthesize the provided research nodes into a professional Markdown report.

# # # # Structure:
# # # # 1. Executive Summary
# # # # 2. Detailed Findings (grouped by topic)
# # # # 3. Bibliography (list all unique sources)

# # # # Constraint: Use ONLY the provided findings. If certain info is missing, say so.
# # # # """

# # # #     user_prompt = f"""
# # # # ### RESEARCH FINDINGS FROM DATABASE ###
# # # # {full_context}

# # # # ### ORIGINAL BRIEF ###
# # # # {json.dumps(research_brief, indent=2)}

# # # # Please generate the final report now in Markdown format.
# # # # """

# # # #     # 3. Call Ollama
# # # #     try:
# # # #         final_report = chat_with_llm(system_prompt=system_prompt, user_prompt=user_prompt)
# # # #         state["final_report"] = final_report
        
# # # #         # Save the final report back to the mission table
# # # #         conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # # #         cur = conn.cursor()
# # # #         cur.execute(
# # # #             "UPDATE research_missions SET status = 'completed' WHERE id = %s",
# # # #             (mission_id,)
# # # #         )
# # # #         conn.commit()
# # # #         cur.close()
# # # #         conn.close()
        
# # # #     except Exception as e:
# # # #         state["final_report"] = f"Synthesis failed: {e}"

# # # #     print("\n🎉 Synthesis complete! Final report stored in state and mission marked as complete.")
# # # #     return state
# # # import psycopg2
# # # import json
# # # from typing import Dict, Any, List
# # # from my_llm.ollama_client import chat_with_llm

# # # ResearchState = Dict[str, Any]

# # # def run_synthesis(state: ResearchState) -> ResearchState:
# # #     print("\n✍️ Running Synthesis Node (Merging Memory & Database Findings)...")

# # #     mission_id = state.get("mission_id")
# # #     research_brief = state.get("research_brief", {})
# # #     target = state.get("target", "the subject")
# # #     report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")
    
# # #     # --- 1. COLLECT DATA FROM FAST MODE (In-Memory State) ---
# # #     # This comes from the run_fast_research parallel workers
# # #     fast_findings = state.get("raw_research_output", [])
# # #     fast_context_blocks = []
    
# # #     for item in fast_findings:
# # #         if item.get("status") == "success":
# # #             task = item.get("task", "General Task")
# # #             result = item.get("result", "")
# # #             fast_context_blocks.append(f"TOPIC: {task}\nFINDING: {result}\nSOURCE: Fast Parallel Agent\n---")

# # #     # --- 2. COLLECT DATA FROM DEEP MODE (Postgres Database) ---
# # #     # This comes from the run_actual_research sequential agent
# # #     db_context_blocks = []
# # #     if mission_id:
# # #         try:
# # #             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # #             cur = conn.cursor()
            
# # #             cur.execute(
# # #                 "SELECT topic, content, source_url FROM research_nodes WHERE mission_id = %s",
# # #                 (mission_id,)
# # #             )
# # #             db_rows = cur.fetchall()
            
# # #             for row in db_rows:
# # #                 db_context_blocks.append(f"TOPIC: {row[0]}\nFINDING: {row[1]}\nSOURCE: {row[2]}\n---")
            
# # #             cur.close()
# # #             conn.close()
# # #         except Exception as e:
# # #             print(f"⚠️ Postgres Fetch Warning: {e}")

# # #     # --- 3. MERGE CONTEXT ---
# # #     combined_context = "\n".join(fast_context_blocks + db_context_blocks)
    
# # #     if not combined_context.strip():
# # #         combined_context = "No research findings were collected from either Fast or Deep agents."

# # #     # --- 4. CONSTRUCT THE SYNTHESIS PROMPT ---
# # #     system_prompt = f"""
# # # You are a Senior Research Analyst writing the '{report_name}' for {target}.
# # # Your goal is to synthesize ALL provided findings into a professional Markdown report.

# # # Instructions:
# # # 1. Executive Summary: High-level overview of findings.
# # # 2. Detailed Analysis: Group findings logically by theme or sub-question.
# # # 3. Citations: Reference the 'SOURCE' provided in the context for each major fact.
# # # 4. Gaps: If information is missing based on the brief, specify it.

# # # Constraint: Use ONLY the provided findings. Use clean Markdown headers and lists.
# # # """

# # #     user_prompt = f"""
# # # ### INTEGRATED RESEARCH CONTEXT (Parallel & Persistent) ###
# # # {combined_context}

# # # ### ORIGINAL MISSION BRIEF ###
# # # {json.dumps(research_brief, indent=2)}

# # # Please generate the final comprehensive report now.
# # # """

# # #     # --- 5. GENERATE & PERSIST ---
# # #     try:
# # #         final_report = chat_with_llm(system_prompt=system_prompt, user_prompt=user_prompt)
# # #         state["final_report"] = final_report
        
# # #         # Update Mission Status if mission_id exists
# # #         if mission_id:
# # #             try:
# # #                 conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# # #                 cur = conn.cursor()
# # #                 cur.execute(
# # #                     "UPDATE research_missions SET status = 'completed' WHERE id = %s",
# # #                     (mission_id,)
# # #                 )
# # #                 conn.commit()
# # #                 cur.close()
# # #                 conn.close()
# # #             except Exception as e:
# # #                 print(f"⚠️ Could not update mission status in DB: {e}")
        
# # #     except Exception as e:
# # #         state["final_report"] = f"Synthesis failed during LLM generation: {e}"

# # #     print(f"\n🎉 Synthesis complete! Compiled {len(fast_context_blocks)} fast results and {len(db_context_blocks)} deep results.")
# # #     return state
# # import psycopg2
# # import json
# # from typing import Dict, Any, List
# # from my_llm.ollama_client import chat_with_llm

# # ResearchState = Dict[str, Any]

# # def run_synthesis(state: ResearchState) -> ResearchState:
# #     print("\n✍️ Running Synthesis Node (Merging Parallel & Database Findings)...")

# #     mission_id = state.get("mission_id")
# #     research_brief = state.get("research_brief", {})
# #     # Use target from state (Fast) or brief (Deep)
# #     target = state.get("target") or research_brief.get("target", "the subject")
# #     report_name = research_brief.get("settings", {}).get("name", "Research Report")
    
# #     context_blocks = []

# #     # --- 1. COLLECT DATA FROM FAST MODE (In-Memory State) ---
# #     # Fast Agent stores results as a list of dicts in raw_research_output
# #     fast_findings = state.get("raw_research_output", [])
# #     if isinstance(fast_findings, list):
# #         for item in fast_findings:
# #             # Handle different possible keys from fast worker
# #             query = item.get("query") or item.get("task", "General Task")
# #             content = item.get("content") or item.get("result", "")
# #             source = item.get("source", "Web Search")
            
# #             if content:
# #                 context_blocks.append(f"TOPIC: {query}\nFINDING: {content}\nSOURCE: {source}\n---")

# #     # --- 2. COLLECT DATA FROM DEEP MODE (Postgres Database) ---
# #     if mission_id:
# #         try:
# #             conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# #             cur = conn.cursor()
# #             cur.execute(
# #                 "SELECT topic, content, source_url FROM research_nodes WHERE mission_id = %s",
# #                 (mission_id,)
# #             )
# #             db_rows = cur.fetchall()
# #             for row in db_rows:
# #                 context_blocks.append(f"TOPIC: {row[0]}\nFINDING: {row[1]}\nSOURCE: {row[2]}\n---")
# #             cur.close()
# #             conn.close()
# #         except Exception as e:
# #             print(f"⚠️ Postgres Fetch Warning: {e}")

# #     # --- 3. MERGE & VALIDATE ---
# #     full_context = "\n".join(context_blocks)
    
# #     if not full_context.strip():
# #         print("⚠️ No data found in State or DB!")
# #         state["final_report"] = "## Error\nNo research findings were collected. Please check search agent logs."
# #         return state

# #     # --- 4. CONSTRUCT THE SYNTHESIS PROMPT ---
# #     system_prompt = f"""
# # You are a Senior Research Analyst. Write a professional Markdown report titled '{report_name}' regarding {target}.
# # Merge all findings into a cohesive narrative. 

# # Structure:
# # 1. Executive Summary
# # 2. Detailed Findings (Grouped by sub-questions or themes)
# # 3. Key Recommendations (if applicable)
# # 4. Sources (List all unique links/sources provided)

# # Constraint: Use ONLY the provided context. If a specific part of the brief wasn't answered by the data, mark it as 'Information not available'.
# # """

# #     user_prompt = f"""
# # ### RESEARCH CONTEXT ###
# # {full_context}

# # ### RESEARCH BRIEF / GOALS ###
# # {json.dumps(research_brief, indent=2) if research_brief else "Goal: " + state.get('user_query', 'General Research')}

# # Generate the final report in clean Markdown format.
# # """

# #     # --- 5. GENERATE & FINALIZE ---
# #     try:
# #         final_report = chat_with_llm(system_prompt=system_prompt, user_prompt=user_prompt)
# #         state["final_report"] = final_report
        
# #         # Mark mission as complete in DB if it's a Deep mission
# #         if mission_id:
# #             _mark_mission_complete(mission_id)
            
# #     except Exception as e:
# #         print(f"❌ Synthesis LLM Error: {e}")
# #         state["final_report"] = f"Synthesis failed: {e}"

# #     print(f"🎉 Synthesis complete. Final report generated using {len(context_blocks)} data points.")
# #     return state

# # def _mark_mission_complete(mission_id: int):
# #     try:
# #         conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
# #         cur = conn.cursor()
# #         cur.execute("UPDATE research_missions SET status = 'completed' WHERE id = %s", (mission_id,))
# #         conn.commit()
# #         cur.close()
# #         conn.close()
# #     except Exception as e:
# #         print(f"⚠️ Could not update mission status: {e}")
# import psycopg2
# import json
# from typing import Dict, Any, List
# from my_llm.ollama_client import chat_with_llm
# from datetime import datetime
# ResearchState = Dict[str, Any]

# def run_synthesis(state: ResearchState) -> ResearchState:
#     # Determine the mode (Fast vs Deep)
#     mode = state.get("research_mode", "fast")
#     mission_id = state.get("mission_id")
#     research_brief = state.get("research_brief", {})
#     target = state.get("target") or research_brief.get("target", "the subject")
#     current_date = datetime.now().strftime("%B %d, %Y")
#     print(f"\n✍️ Running Synthesis Node ({mode.upper()} mode)...")

#     # --- 1. COLLECT DATA ---
#     context_blocks = []
    
#     # Mode-specific data gathering
#     if mode == "fast":
#         fast_findings = state.get("raw_research_output", [])
#         if isinstance(fast_findings, list):
#             for item in fast_findings:
#                 query = item.get("query") or item.get("task", "General Task")
#                 content = item.get("content") or item.get("result", "")
#                 if content:
#                     context_blocks.append(f"Q: {query}\nA: {content}")
#     else:
#         # Deep mode: Pull from Postgres
#         if mission_id:
#             try:
#                 conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
#                 cur = conn.cursor()
#                 cur.execute(
#                     "SELECT topic, content, source_url FROM research_nodes WHERE mission_id = %s",
#                     (mission_id,)
#                 )
#                 db_rows = cur.fetchall()
#                 for row in db_rows:
#                     context_blocks.append(f"TOPIC: {row[0]}\nFINDING: {row[1]}\nSOURCE: {row[2]}")
#                 cur.close()
#                 conn.close()
#             except Exception as e:
#                 print(f"⚠️ Postgres Fetch Warning: {e}")

#     full_context = "\n---\n".join(context_blocks)
    
#     if not full_context.strip():
#         state["final_report"] = "No research findings were collected."
#         return state

#     # --- 2. CONDITIONAL PROMPT LOGIC ---
#     if mode == "fast":
#         # SHORT AND CRISP PROMPT
#         system_prompt = f"You are a helpful assistant. Provide a very short, crisp, and bulleted summary for {target}. Focus only on the most vital facts."
#         user_prompt = f"Summarize this context into a few punchy bullet points:\n\n{full_context}"
#     else:
#         # FULL DEEP REPORT PROMPT
        
#         report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")
#         system_prompt = f"""
#         You are a Senior Research Analyst. Write a professional, detailed Markdown report titled '{report_name}' for {target}.
#         CURRENT DATE: {current_date}
#         Structure:
#         1. Executive Summary
#         2. Deep Dive Findings (per sub-question)
#         3. Analysis & Implications
#         4. Comprehensive Bibliography
        
#         Constraint: Use ONLY the provided context and cite sources.
#         """
#         user_prompt = f"### RESEARCH CONTEXT ###\n{full_context}\n\n### BRIEF ###\n{json.dumps(research_brief, indent=2)}\n\nGenerate the full professional report."

#     # --- 3. GENERATE ---
#     try:
#         final_output = chat_with_llm(system_prompt=system_prompt, user_prompt=user_prompt)
#         state["final_report"] = final_output
        
#         # Cleanup for Deep Mode
#         if mode == "deep" and mission_id:
#             _mark_mission_complete(mission_id)
            
#     except Exception as e:
#         print(f"❌ Synthesis Error: {e}")
#         state["final_report"] = f"Synthesis failed: {e}"

#     print(f"🎉 Synthesis complete in {mode} mode.")
#     return state

# def _mark_mission_complete(mission_id: int):
#     try:
#         conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
#         cur = conn.cursor()
#         cur.execute("UPDATE research_missions SET status = 'completed' WHERE mission_id = %s", (mission_id,))
#         conn.commit()
#         cur.close()
#         conn.close()
#     except Exception as e:
#         print(f"⚠️ Status Update Error: {e}")
import psycopg2
import json
from typing import Dict, Any, List
from my_llm.ollama_client import chat_with_llm
from datetime import datetime

# --- NEW: Simple Token Approximation Utility ---
def limit_string_tokens(text: str, max_chars: int = 400000) -> str:
    """
    Roughly limits the context size. 400k characters is approx 100k tokens.
    This prevents the '400 - context_length_exceeded' error.
    """
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... [TRUNCATED DUE TO CONTEXT LIMITS] ..."
    return text

def run_synthesis(state: Dict[str, Any]) -> Dict[str, Any]:
    mode = state.get("research_mode", "fast")
    mission_id = state.get("mission_id")
    research_brief = state.get("research_brief", {})
    target = state.get("target") or research_brief.get("target", "the subject")
    current_date = datetime.now().strftime("%B %d, %Y")
    
    print(f"\n✍️ Running Synthesis Node ({mode.upper()} mode)...")

    # --- 1. COLLECT DATA ---
    context_blocks = []
    
    if mode == "fast":
        fast_findings = state.get("raw_research_output", [])
        if isinstance(fast_findings, list):
            for item in fast_findings:
                query = item.get("query") or item.get("task", "General Task")
                content = item.get("content") or item.get("result", "")
                if content:
                    context_blocks.append(f"Q: {query}\nA: {content}")
    else:
        if mission_id:
            try:
                conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
                cur = conn.cursor()
                cur.execute(
                    "SELECT topic, content, source_url FROM research_nodes WHERE mission_id = %s",
                    (mission_id,)
                )
                db_rows = cur.fetchall()
                for row in db_rows:
                    # Prune each block slightly to ensure essential info is kept
                    context_blocks.append(f"TOPIC: {row[0]}\nFINDING: {row[1]}\nSOURCE: {row[2]}")
                cur.close()
                conn.close()
            except Exception as e:
                print(f"⚠️ Postgres Fetch Warning: {e}")

    # --- 2. APPLY CONTEXT TRIMMER ---
    # We join everything then force a character limit to stay under the 128k token cap
    full_context = "\n---\n".join(context_blocks)
    
    # 400,000 characters is a safe upper bound for a 128k token model 
    # to allow room for the instructions and the generated report.
    full_context = limit_string_tokens(full_context, max_chars=350000) 
    
    if not full_context.strip():
        state["final_report"] = "No research findings were collected."
        return state

    # --- 3. CONDITIONAL PROMPT LOGIC ---
    if mode == "fast":
        system_prompt = f"You are a helpful assistant. Provide a very short, crisp, and bulleted summary for {target}. Focus only on the most vital facts."
        user_prompt = f"Summarize this context into a few punchy bullet points:\n\n{full_context}"
    else:
        report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")
        system_prompt = f"""
        You are a Senior Research Analyst. Write a professional, detailed Markdown report titled '{report_name}' for {target}.
        CURRENT DATE: {current_date}
        Structure:
        1. Executive Summary
        2. Deep Dive Findings (per sub-question)
        3. Analysis & Implications
        4. Comprehensive Bibliography
        
        Constraint: Use ONLY the provided context and cite sources.
        """
        user_prompt = f"### RESEARCH CONTEXT ###\n{full_context}\n\n### BRIEF ###\n{json.dumps(research_brief, indent=2)}\n\nGenerate the full professional report."

    # --- 4. GENERATE WITH SAFETY ---
    try:
        # We pass the trimmed context directly to the LLM
        final_output = chat_with_llm(system_prompt=system_prompt, user_prompt=user_prompt)
        state["final_report"] = final_output
        
        if mode == "deep" and mission_id:
            _mark_mission_complete(mission_id)
            
    except Exception as e:
        # If it STILL fails due to context, we try one last ultra-aggressive trim
        if "context_length_exceeded" in str(e).lower():
            print("🚨 Emergency Trimming Triggered...")
            ultra_trimmed = limit_string_tokens(full_context, max_chars=100000)
            final_output = chat_with_llm(system_prompt=system_prompt, user_prompt=f"[EMERGENCY TRIM APPLIED]\n{ultra_trimmed}")
            state["final_report"] = final_output
        else:
            print(f"❌ Synthesis Error: {e}")
            state["final_report"] = f"Synthesis failed: {e}"

    print(f"🎉 Synthesis complete in {mode} mode.")
    return state

def _mark_mission_complete(mission_id: str):
    try:
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        cur = conn.cursor()
        cur.execute("UPDATE research_missions SET status = 'completed' WHERE id = %s", (str(mission_id),))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Status Update Error: {e}")