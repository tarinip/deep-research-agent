# # # nodes/reflection.py

# from typing import Dict, Any, List, Tuple
# # from my_llm.ollama_client import ollama_chat 
# ResearchState = Dict[str, Any]

# # def run_reflection_tool(state: ResearchState) -> ResearchState:
# #     """
# #     Critiques the 'raw_research_output' and determines the next step.
# #     The decision is whether to loop back to research or proceed to synthesis.
# #     """
# #     print("\n🧠 Running Reflection/Critique Tool...")

# #     # 1. Get Data
# #     raw_results: List[Dict] = state.get("raw_research_output", [])
# #     brief = state.get("research_brief", {})
    
# #     # Simple Mock Logic: Check if at least 75% of queries succeeded and returned some organic results.
# #     successful_queries = 0
# #     total_queries = len(raw_results)

# #     for query_data in raw_results:
# #         # A simple check for success status and the presence of organic results
# #         if query_data.get('status') == 'success' and query_data.get('raw_json_result', {}).get('organic_results'):
# #             successful_queries += 1

# #     data_sufficiency_ratio = successful_queries / total_queries if total_queries > 0 else 0
    
# #     # --- DECISION LOGIC ---
# #     if data_sufficiency_ratio < 0.75 and total_queries > 0:
# #         is_sufficient = False
# #         next_step = "research" # Loop back to research
# #         log = f"Critique: Only {successful_queries}/{total_queries} queries were successful. Insufficient data. Re-running research."
# #     else:
# #         is_sufficient = True
# #         next_step = "synthesis" # Proceed to synthesis
# #         log = "Critique: Sufficient data gathered (>=75% success rate). Proceeding to synthesis."

# #     # 3. Update the state for the next graph step
# #     state["reflection_log"] = log
# #     state["is_data_sufficient"] = is_sufficient
# #     state["next_node"] = next_step # This drives the conditional edge

# #     print(f"   -> {log}")
    
# #     return state
# # nodes/reflection.py

# def run_reflection_tool(state: ResearchState) -> ResearchState:
#     print("\n🧠 Running Reflection/Critique Tool...")

#     raw_results: List[Dict] = state.get("raw_research_output", [])
    
#     successful_queries = 0
#     total_queries = len(raw_results)

#     for query_data in raw_results:
#         # FIX: Check for the 'results' key which you created in research.py
#         # Also check for 'knowledge_graph' as a backup success metric
#         has_organic = len(query_data.get('results', [])) > 0
#         has_kg = bool(query_data.get('knowledge_graph'))
        
#         if has_organic or has_kg:
#             successful_queries += 1

#     # Calculate ratio
#     data_sufficiency_ratio = successful_queries / total_queries if total_queries > 0 else 0
    
#     # Logic to prevent infinite loops: Max 3 retries
#     # You can add a 'retry_count' to your state to force completion
#     retry_count = state.get("retry_count", 0)
    
#     if data_sufficiency_ratio < 0.75 and retry_count < 3:
#         is_sufficient = False
#         next_step = "research"
#         state["retry_count"] = retry_count + 1
#         log = f"Critique: {successful_queries}/{total_queries} success. Retrying (Attempt {state['retry_count']})."
#     else:
#         is_sufficient = True
#         next_step = "synthesis"
#         log = f"Critique: Proceeding with {successful_queries}/{total_queries} successful queries."

#     state["reflection_log"] = log
#     state["is_data_sufficient"] = is_sufficient
#     state["next_node"] = next_step 

#     print(f"   -> {log}")
#     return state
# nodes/reflection.py
import psycopg2
from typing import Dict, Any, List
from my_llm.ollama_client import chat_with_llm
from pgvector.psycopg2 import register_vector

ResearchState = Dict[str, Any]

def run_reflection_tool(state: ResearchState) -> ResearchState:
    print("\n🧠 Running Qualitative Reflection...")
    
    mission_id = state.get("mission_id")
    brief = state.get("research_brief", {})
    target = brief.get("target", "the subject")
    
    # 1. Connect to Postgres to see what we've gathered
    conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
    register_vector(conn)
    cur = conn.cursor()
    
    cur.execute(
        "SELECT topic, content FROM research_nodes WHERE mission_id = %s", 
        (mission_id,)
    )
    findings = cur.fetchall()
    context_summary = "\n".join([f"Topic: {f[0]}\nFact: {f[1][:200]}..." for f in findings])

    # 2. Ask Ollama to find "Gaps"
    system_prompt = f"""
    You are a Senior Research Auditor. 
    Review the gathered facts for '{target}' against the original research goals.
    Goals: {brief.get('summary')}
    
    Findings so far:
    {context_summary}
    
    Task: Identify if there are critical missing pieces.
    If yes, output: "MISSING: <topic>"
    If no, output: "SUFFICIENT"
    """
    
    reflection_raw = chat_with_llm(system_prompt=system_prompt, user_prompt="Analyze for gaps.")
    
    # 3. Logic for looping or finishing
    retry_count = state.get("retry_count", 0)
    
    if "MISSING:" in reflection_raw and retry_count < 2:
        # Extract the new gap to research
        new_gap = reflection_raw.split("MISSING:")[1].strip().split("\n")[0]
        
        # Inject the gap back into the tasks table for the Research Node to find
        cur.execute(
            "INSERT INTO research_tasks (mission_id, question, status) VALUES (%s, %s, %s)",
            (mission_id, f"Deep dive into {new_gap}", "pending")
        )
        conn.commit()
        
        state["next_node"] = "research"
        state["retry_count"] = retry_count + 1
        log = f"Gap identified: {new_gap}. Re-routing to Research."
    else:
        state["next_node"] = "synthesis"
        log = "No major gaps found or max retries reached. Proceeding to Synthesis."

    cur.close()
    conn.close()
    
    state["reflection_log"] = log
    print(f"   -> {log}")
    return state