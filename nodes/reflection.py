# # # # nodes/reflection.py

# # from typing import Dict, Any, List, Tuple
# # # from my_llm.ollama_client import ollama_chat 
# # ResearchState = Dict[str, Any]

# # # def run_reflection_tool(state: ResearchState) -> ResearchState:
# # #     """
# # #     Critiques the 'raw_research_output' and determines the next step.
# # #     The decision is whether to loop back to research or proceed to synthesis.
# # #     """
# # #     print("\n🧠 Running Reflection/Critique Tool...")

# # #     # 1. Get Data
# # #     raw_results: List[Dict] = state.get("raw_research_output", [])
# # #     brief = state.get("research_brief", {})
    
# # #     # Simple Mock Logic: Check if at least 75% of queries succeeded and returned some organic results.
# # #     successful_queries = 0
# # #     total_queries = len(raw_results)

# # #     for query_data in raw_results:
# # #         # A simple check for success status and the presence of organic results
# # #         if query_data.get('status') == 'success' and query_data.get('raw_json_result', {}).get('organic_results'):
# # #             successful_queries += 1

# # #     data_sufficiency_ratio = successful_queries / total_queries if total_queries > 0 else 0
    
# # #     # --- DECISION LOGIC ---
# # #     if data_sufficiency_ratio < 0.75 and total_queries > 0:
# # #         is_sufficient = False
# # #         next_step = "research" # Loop back to research
# # #         log = f"Critique: Only {successful_queries}/{total_queries} queries were successful. Insufficient data. Re-running research."
# # #     else:
# # #         is_sufficient = True
# # #         next_step = "synthesis" # Proceed to synthesis
# # #         log = "Critique: Sufficient data gathered (>=75% success rate). Proceeding to synthesis."

# # #     # 3. Update the state for the next graph step
# # #     state["reflection_log"] = log
# # #     state["is_data_sufficient"] = is_sufficient
# # #     state["next_node"] = next_step # This drives the conditional edge

# # #     print(f"   -> {log}")
    
# # #     return state
# # # nodes/reflection.py

# # def run_reflection_tool(state: ResearchState) -> ResearchState:
# #     print("\n🧠 Running Reflection/Critique Tool...")

# #     raw_results: List[Dict] = state.get("raw_research_output", [])
    
# #     successful_queries = 0
# #     total_queries = len(raw_results)

# #     for query_data in raw_results:
# #         # FIX: Check for the 'results' key which you created in research.py
# #         # Also check for 'knowledge_graph' as a backup success metric
# #         has_organic = len(query_data.get('results', [])) > 0
# #         has_kg = bool(query_data.get('knowledge_graph'))
        
# #         if has_organic or has_kg:
# #             successful_queries += 1

# #     # Calculate ratio
# #     data_sufficiency_ratio = successful_queries / total_queries if total_queries > 0 else 0
    
# #     # Logic to prevent infinite loops: Max 3 retries
# #     # You can add a 'retry_count' to your state to force completion
# #     retry_count = state.get("retry_count", 0)
    
# #     if data_sufficiency_ratio < 0.75 and retry_count < 3:
# #         is_sufficient = False
# #         next_step = "research"
# #         state["retry_count"] = retry_count + 1
# #         log = f"Critique: {successful_queries}/{total_queries} success. Retrying (Attempt {state['retry_count']})."
# #     else:
# #         is_sufficient = True
# #         next_step = "synthesis"
# #         log = f"Critique: Proceeding with {successful_queries}/{total_queries} successful queries."

# #     state["reflection_log"] = log
# #     state["is_data_sufficient"] = is_sufficient
# #     state["next_node"] = next_step 

# #     print(f"   -> {log}")
# #     return state
# # nodes/reflection.py
# import psycopg2
# from typing import Dict, Any, List
# from my_llm.ollama_client import chat_with_llm
# from pgvector.psycopg2 import register_vector

# ResearchState = Dict[str, Any]

# def run_reflection_tool(state: ResearchState) -> ResearchState:
#     print("\n🧠 Running Qualitative Reflection...")
    
#     mission_id = state.get("mission_id")
#     brief = state.get("research_brief", {})
#     target = brief.get("target", "the subject")
    
#     # 1. Connect to Postgres to see what we've gathered
#     conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
#     register_vector(conn)
#     cur = conn.cursor()
    
#     cur.execute(
#         "SELECT topic, content FROM research_nodes WHERE id = %s", 
#         (mission_id,)
#     )
#     findings = cur.fetchall()
#     context_summary = "\n".join([f"Topic: {f[0]}\nFact: {f[1][:200]}..." for f in findings])

#     # 2. Ask Ollama to find "Gaps"
#     system_prompt = f"""
#     You are a Senior Research Auditor. 
#     Review the gathered facts for '{target}' against the original research goals.
#     Goals: {brief.get('summary')}
    
#     Findings so far:
#     {context_summary}
    
#     Task: Identify if there are critical missing pieces.
#     If yes, output: "MISSING: <topic>"
#     If no, output: "SUFFICIENT"
#     """
    
#     reflection_raw = chat_with_llm(system_prompt=system_prompt, user_prompt="Analyze for gaps.")
    
#     # 3. Logic for looping or finishing
#     retry_count = state.get("retry_count", 0)
    
#     if "MISSING:" in reflection_raw and retry_count < 2:
#         # Extract the new gap to research
#         new_gap = reflection_raw.split("MISSING:")[1].strip().split("\n")[0]
        
#         # Inject the gap back into the tasks table for the Research Node to find
#         cur.execute(
#             "INSERT INTO research_tasks (id, question, status) VALUES (%s, %s, %s)",
#             (mission_id, f"Deep dive into {new_gap}", "pending")
#         )
#         conn.commit()
        
#         state["next_node"] = "research"
#         state["retry_count"] = retry_count + 1
#         log = f"Gap identified: {new_gap}. Re-routing to Research."
#     else:
#         state["next_node"] = "synthesis"
#         log = "No major gaps found or max retries reached. Proceeding to Synthesis."

#     cur.close()
#     conn.close()
    
#     state["reflection_log"] = log
#     print(f"   -> {log}")
#     return state
import psycopg2
from typing import Dict, Any, List
# Use LangChain ChatOpenAI for consistency with your research node if you prefer, 
# or keep your ollama_client if that is your preference.
from langchain_openai import ChatOpenAI 
from pgvector.psycopg2 import register_vector
from datetime import datetime
ResearchState = Dict[str, Any]

def run_reflection_tool(state: ResearchState) -> ResearchState:
    print("\n🧠 Running Qualitative Reflection...")
    
    mission_id = state.get("mission_id")
    # FIX: Ensure we handle keys safely
    brief = state.get("research_brief", {})
    target = state.get("target", "the subject") # State usually has 'target' directly
    
    # 1. Database Connection
    try:
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        register_vector(conn)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Reflection DB Error: {e}")
        state["next_node"] = "synthesis"
        return state
    
    # 2. Check current findings
    cur.execute(
        "SELECT topic, content FROM research_nodes WHERE mission_id = %s", 
        (mission_id,)
    )
    findings = cur.fetchall()
    
    # If we have no findings at all, we must check if we've failed everything
    if not findings:
        cur.execute("SELECT count(*) FROM research_tasks WHERE id = %s AND status = 'failed'", (mission_id,))
        failed_count = cur.fetchone()[0]
        if failed_count > 0:
            print("   ⚠️ No findings found, but tasks have failed. Stopping loop.")
            state["next_node"] = "synthesis"
            return state

    context_summary = "\n".join([f"Topic: {f[0]}\nFact: {f[1][:150]}..." for f in findings])

    # 3. Use LLM to Audit for Gaps
    # Using a slightly stricter prompt to prevent the LLM from being too "curious"
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    current_date = datetime.now().strftime("%B %d, %Y")
    system_prompt = f"""
    You are a Senior Research Auditor. 
    Review gathered facts for '{target}'. Original Goal: {brief.get('summary', 'General Research')}
    CURRENT DATE: {current_date}
    Findings so far:
    {context_summary}
    
    Task: Is there a CRITICAL missing piece that can actually be found online?
    - If a topic has been tried but returned no info, do NOT mark it missing.
    - If sufficient, output: SUFFICIENT
    - If critical gap exists, output: MISSING: <one_specific_topic>
    """
    
    reflection_res = llm.invoke(system_prompt).content
    
    # 4. Loop Control
    retry_count = state.get("retry_count", 0)
    max_retries = 2 # Strictly limit retries to prevent GraphRecursionError
    
    if "MISSING:" in reflection_res and retry_count < max_retries:
        new_gap = reflection_res.split("MISSING:")[1].strip().split("\n")[0]
        
        # SAFETY: Check if we already tried this exact gap to prevent infinite loops
        cur.execute(
            "SELECT count(*) FROM research_tasks WHERE mission_id = %s AND question ILIKE %s",
            (mission_id, f"%{new_gap}%")
        )
        already_tried = cur.fetchone()[0]

        if already_tried == 0:
            cur.execute(
                "INSERT INTO research_tasks (mission_id, question, status) VALUES (%s, %s, %s)",
                (mission_id, f"Researching gap: {new_gap}", "pending")
            )
            conn.commit()
            state["next_node"] = "deep_research"
            state["retry_count"] = retry_count + 1
            log = f"Gap identified: {new_gap}. Re-routing to Research (Attempt {state['retry_count']})."
        else:
            state["next_node"] = "synthesis"
            log = f"Gap '{new_gap}' was already attempted. Proceeding to Synthesis."
    else:
        state["next_node"] = "synthesis"
        log = "No major gaps found or max retries reached. Proceeding to Synthesis."

    cur.close()
    conn.close()
    
    state["reflection_log"] = log
    print(f"   -> {log}")
    return state