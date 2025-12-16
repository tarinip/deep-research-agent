# nodes/reflection.py

from typing import Dict, Any, List, Tuple
# from my_llm.ollama_client import ollama_chat 
ResearchState = Dict[str, Any]

def run_reflection_tool(state: ResearchState) -> ResearchState:
    """
    Critiques the 'raw_research_output' and determines the next step.
    The decision is whether to loop back to research or proceed to synthesis.
    """
    print("\n🧠 Running Reflection/Critique Tool...")

    # 1. Get Data
    raw_results: List[Dict] = state.get("raw_research_output", [])
    brief = state.get("research_brief", {})
    
    # Simple Mock Logic: Check if at least 75% of queries succeeded and returned some organic results.
    successful_queries = 0
    total_queries = len(raw_results)

    for query_data in raw_results:
        # A simple check for success status and the presence of organic results
        if query_data.get('status') == 'success' and query_data.get('raw_json_result', {}).get('organic_results'):
            successful_queries += 1

    data_sufficiency_ratio = successful_queries / total_queries if total_queries > 0 else 0
    
    # --- DECISION LOGIC ---
    if data_sufficiency_ratio < 0.75 and total_queries > 0:
        is_sufficient = False
        next_step = "research" # Loop back to research
        log = f"Critique: Only {successful_queries}/{total_queries} queries were successful. Insufficient data. Re-running research."
    else:
        is_sufficient = True
        next_step = "synthesis" # Proceed to synthesis
        log = "Critique: Sufficient data gathered (>=75% success rate). Proceeding to synthesis."

    # 3. Update the state for the next graph step
    state["reflection_log"] = log
    state["is_data_sufficient"] = is_sufficient
    state["next_node"] = next_step # This drives the conditional edge

    print(f"   -> {log}")
    
    return state