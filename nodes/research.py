# nodes/research.py

import os
from typing import Dict, Any, List, Optional
import json
# Import the correct wrapper for SerpAPI
from langchain_community.utilities import SerpAPIWrapper 

# Assume ResearchState is defined/imported from the main file for type hinting
ResearchState = Dict[str, Any]


def run_actual_research(state: ResearchState) -> ResearchState:
    """
    Executes the search strategy defined in the research brief using SerpAPI.
    """
    print("\n🔍 Executing Research Node with SerpAPI...")

    # 1. Get the plan from the state
    research_brief = state.get("research_brief", {})
    sub_questions: List[str] = research_brief.get("sub_questions", [])
    
    if not sub_questions:
        print("⚠️ Warning: No sub-questions found in the brief. Aborting research.")
        state["raw_research_output"] = [{"error": "No sub-questions in brief."}]
        state["next_node"] = "synthesis" # Fallback to prevent immediate failure
        return state

    # 2. Initialize the Search Tool
    try:
        # SerpAPIWrapper automatically looks for the SERPAPI_API_KEY env var.
        # It runs the query and returns a raw dictionary result.
        search = SerpAPIWrapper(params={"engine": "google", "num": 5}) # num=5 for 5 results
    except Exception as e:
        error_msg = f"Error initializing SerpAPIWrapper. Check SERPAPI_API_KEY environment variable: {e}"
        print(f"Error: {error_msg}")
        state["raw_research_output"] = [{"error": error_msg}]
        state["next_node"] = "synthesis" 
        return state
    
    all_raw_results: List[Dict[str, Any]] = []

    # 3. Execute Searches for each sub-question
    print(f"   -> Running {len(sub_questions)} queries...")
    for i, question in enumerate(sub_questions):
        print(f"      -> Query {i+1}/{len(sub_questions)}: {question[:70]}...")
        try:
            # SerpAPIWrapper's results() method returns the raw JSON from SerpAPI.
            # This raw JSON typically includes organic results, knowledge graphs, etc.
            raw_json_result = search.results(question) 
            all_raw_results.append({
                "query": question,
                "raw_json_result": raw_json_result,
                "status": "success"
            })
        except Exception as e:
            print(f"      -> Search failed for query '{question}': {e}")
            all_raw_results.append({"query": question, "raw_json_result": {}, "status": "failed", "error": str(e)})

    # 4. Update the state with raw results
    state["raw_research_output"] = all_raw_results
    
    # 5. Signal the next node: Reflection/Critique
    state["next_node"] = "reflection"

    print("\n✅ Research execution complete. Passing to Reflection tool.")
    return state