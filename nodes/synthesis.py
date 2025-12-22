# # # nodes/synthesis.py

# # from typing import Dict, Any, List, Optional
# # import json
# # from my_llm.ollama_client import ollama_chat # Assumed import for your LLM client
# # # from utils.json_sanitizer import sanitize_json_string # Not strictly needed here

# # ResearchState = Dict[str, Any]

# # def run_synthesis(state: ResearchState) -> ResearchState:
# #     """
# #     Analyzes the raw research data against the brief and generates the final report
# #     using an LLM for synthesis. 

# # [Image of RAG process diagram]

# #     """
# #     print("\n✍️ Running Synthesis Node (Generating Final Report)...")

# #     # 1. Get all necessary components from the state
# #     research_brief: Dict[str, Any] = state.get("research_brief", {})
# #     raw_results: List[Dict] = state.get("raw_research_output", [])
# #     reflection_log: str = state.get("reflection_log", "No reflection log available.")
    
# #     # 2. Extract, clean, and format the research data (RAG Context)
# #     search_context_list = []
    
# #     for query_data in raw_results:
# #         # Only process successful queries that returned organic results
# #         if query_data.get('status') == 'success' and query_data.get('raw_json_result', {}).get('organic_results'):
            
# #             snippets = []
# #             # Extract just the title, snippet, and source link for the LLM prompt
# #             for result in query_data['raw_json_result']['organic_results']:
# #                 snippets.append({
# #                     "title": result.get('title'),
# #                     "snippet": result.get('snippet'),
# #                     "source": result.get('link')
# #                 })
            
# #             search_context_list.append({
# #                 "query": query_data['query'],
# #                 "results": snippets
# #             })
            
# #     search_context_str = json.dumps(search_context_list, indent=2)


# #     # 3. LLM Prompt Construction (The Synthesis Task)
# # #     system_prompt = """
# # # You are the Final Synthesis Agent. Your task is to use the provided Research Brief 
# # # and Raw Research Context (gathered from search engines) to write a comprehensive, 
# # # final report.

# # # Instructions:
# # # 1. Adhere strictly to the constraints, format, and depth specified in the Research Brief.
# # # 2. Use ONLY the information provided in the Raw Research Context to generate the report. Do not use outside knowledge.
# # # 3. Structure your final output clearly, addressing all 'sub_questions' from the brief.
# # # 4. If the data is insufficient for a sub-question, clearly state the gap based on the reflection log.
# # # 5. Your final output should be a plain text report, suitable for immediate viewing.
# # # """
# #    report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")
# #    target = research_brief.get("target", "the subject")

# #    system_prompt = f"""
# # You are a Senior Research Analyst writing a "{report_name}" about {target}.

# # Instructions:
# # 1. Format: Use clean Markdown (Headers, Bullet points, Bold text).
# # 2. Traceability: When you state a fact, try to include the source title or link from the context provided.
# # 3. Structure: 
# #    - Start with an 'Executive Summary'.
# #    - Create sections for each sub-question.
# #    - Conclude with a 'Sources' section listing the unique links found in the context.

# # Constraint: Use ONLY the provided context. If the data is missing, mark it as 'Information not available'.
# # """
# #    user_prompt = f"""
# # ### RESEARCH BRIEF (The Plan) ###
# # {json.dumps(research_brief, indent=2)}

# # ### RAW RESEARCH CONTEXT (The Data) ###
# # {search_context_str}

# # ### REFLECTION LOG ###
# # {reflection_log}

# # Based on the plan and the context provided, generate the full final report now.
# # """

# #     # 4. Call the LLM (Live Integration)
# #     try:
# #         # Assuming ollama_chat accepts system and user prompts and returns the text response
# #         raw_report = ollama_chat(system_prompt=system_prompt, user_prompt=user_prompt)
# #     except Exception as e:
# #         # Fallback if the LLM call fails
# #         raw_report = f"*** Synthesis Failed: Could not generate report. Error: {e} ***\n\nContext Provided:\n{search_context_str}"


# #     # 5. Update the state with the final result
# #     state["final_report"] = raw_report
    
# #     print("\n🎉 Synthesis complete. Final report generated.")
# #     return state
# # nodes/synthesis.py

# from typing import Dict, Any, List, Optional
# import json
# from my_llm.ollama_client import ollama_chat # Assumed import for your LLM client

# ResearchState = Dict[str, Any]

# def run_synthesis(state: ResearchState) -> ResearchState:
#     """
#     Analyzes the raw research data against the brief and generates the final report
#     using an LLM for synthesis. 
#     """
#     print("\n✍️ Running Synthesis Node (Generating Final Report)...")

#     # 1. Get all necessary components from the state
#     research_brief: Dict[str, Any] = state.get("research_brief", {})
#     raw_results: List[Dict] = state.get("raw_research_output", [])
#     reflection_log: str = state.get("reflection_log", "No reflection log available.")
    
#     # 2. Extract, clean, and format the research data (RAG Context)
#     search_context_list = []
    
#     for query_data in raw_results:
#         if query_data.get('status') == 'success' and query_data.get('raw_json_result', {}).get('organic_results'):
#             snippets = []
#             for result in query_data['raw_json_result']['organic_results']:
#                 snippets.append({
#                     "title": result.get('title'),
#                     "snippet": result.get('snippet'),
#                     "source": result.get('link')
#                 })
            
#             search_context_list.append({
#                 "query": query_data['query'],
#                 "results": snippets
#             })
            
#     search_context_str = json.dumps(search_context_list, indent=2)

#     # 3. LLM Prompt Construction (Corrected Indentation Here)
#     report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")
#     target = research_brief.get("target", "the subject")

#     system_prompt = f"""
# You are a Senior Research Analyst writing a "{report_name}" about {target}.

# Instructions:
# 1. Format: Use clean Markdown (Headers, Bullet points, Bold text).
# 2. Traceability: When you state a fact, try to include the source title or link from the context provided.
# 3. Structure: 
#    - Start with an 'Executive Summary'.
#    - Create sections for each sub-question.
#    - Conclude with a 'Sources' section listing the unique links found in the context.

# Constraint: Use ONLY the provided context. If the data is missing, mark it as 'Information not available'.
# """
#     user_prompt = f"""
# ### RESEARCH BRIEF (The Plan) ###
# {json.dumps(research_brief, indent=2)}

# ### RAW RESEARCH CONTEXT (The Data) ###
# {search_context_str}

# ### REFLECTION LOG ###
# {reflection_log}

# Based on the plan and the context provided, generate the full final report now.
# """

#     # 4. Call the LLM (Live Integration)
#     try:
#         raw_report = ollama_chat(system_prompt=system_prompt, user_prompt=user_prompt)
#     except Exception as e:
#         raw_report = f"*** Synthesis Failed: Could not generate report. Error: {e} ***\n\nContext Provided:\n{search_context_str}"

#     # 5. Update the state with the final result
#     state["final_report"] = raw_report
    
#     print("\n🎉 Synthesis complete. Final report generated.")
#     return state
# nodes/synthesis.py
import psycopg2
import json
from typing import Dict, Any
from my_llm.ollama_client import chat_with_llm

ResearchState = Dict[str, Any]

def run_synthesis(state: ResearchState) -> ResearchState:
    print("\n✍️ Running Synthesis Node (Querying Postgres Memory)...")

    mission_id = state.get("mission_id")
    research_brief = state.get("research_brief", {})
    target = research_brief.get("target", "the subject")
    report_name = research_brief.get("settings", {}).get("name", "Deep Research Report")

    # 1. Pull ALL findings from Postgres for this mission
    try:
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        cur = conn.cursor()
        
        cur.execute(
            "SELECT topic, content, source_url FROM research_nodes WHERE mission_id = %s",
            (mission_id,)
        )
        db_rows = cur.fetchall()
        
        # Format the data for the LLM
        context_blocks = []
        for row in db_rows:
            context_blocks.append(f"TOPIC: {row[0]}\nFINDING: {row[1]}\nSOURCE: {row[2]}\n---")
        
        full_context = "\n".join(context_blocks)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB Error in Synthesis: {e}")
        full_context = "No data found in database."

    # 2. Construct the Prompt
    system_prompt = f"""
You are a Senior Research Analyst writing the '{report_name}' for {target}.
Your goal is to synthesize the provided research nodes into a professional Markdown report.

Structure:
1. Executive Summary
2. Detailed Findings (grouped by topic)
3. Bibliography (list all unique sources)

Constraint: Use ONLY the provided findings. If certain info is missing, say so.
"""

    user_prompt = f"""
### RESEARCH FINDINGS FROM DATABASE ###
{full_context}

### ORIGINAL BRIEF ###
{json.dumps(research_brief, indent=2)}

Please generate the final report now in Markdown format.
"""

    # 3. Call Ollama
    try:
        final_report = chat_with_llm(system_prompt=system_prompt, user_prompt=user_prompt)
        state["final_report"] = final_report
        
        # Save the final report back to the mission table
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        cur = conn.cursor()
        cur.execute(
            "UPDATE research_missions SET status = 'completed' WHERE id = %s",
            (mission_id,)
        )
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        state["final_report"] = f"Synthesis failed: {e}"

    print("\n🎉 Synthesis complete! Final report stored in state and mission marked as complete.")
    return state