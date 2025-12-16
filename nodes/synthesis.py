# nodes/synthesis.py

from typing import Dict, Any, List, Optional
import json
from my_llm.ollama_client import ollama_chat # Assumed import for your LLM client
# from utils.json_sanitizer import sanitize_json_string # Not strictly needed here

ResearchState = Dict[str, Any]

def run_synthesis(state: ResearchState) -> ResearchState:
    """
    Analyzes the raw research data against the brief and generates the final report
    using an LLM for synthesis. 

[Image of RAG process diagram]

    """
    print("\n✍️ Running Synthesis Node (Generating Final Report)...")

    # 1. Get all necessary components from the state
    research_brief: Dict[str, Any] = state.get("research_brief", {})
    raw_results: List[Dict] = state.get("raw_research_output", [])
    reflection_log: str = state.get("reflection_log", "No reflection log available.")
    
    # 2. Extract, clean, and format the research data (RAG Context)
    search_context_list = []
    
    for query_data in raw_results:
        # Only process successful queries that returned organic results
        if query_data.get('status') == 'success' and query_data.get('raw_json_result', {}).get('organic_results'):
            
            snippets = []
            # Extract just the title, snippet, and source link for the LLM prompt
            for result in query_data['raw_json_result']['organic_results']:
                snippets.append({
                    "title": result.get('title'),
                    "snippet": result.get('snippet'),
                    "source": result.get('link')
                })
            
            search_context_list.append({
                "query": query_data['query'],
                "results": snippets
            })
            
    search_context_str = json.dumps(search_context_list, indent=2)


    # 3. LLM Prompt Construction (The Synthesis Task)
    system_prompt = """
You are the Final Synthesis Agent. Your task is to use the provided Research Brief 
and Raw Research Context (gathered from search engines) to write a comprehensive, 
final report.

Instructions:
1. Adhere strictly to the constraints, format, and depth specified in the Research Brief.
2. Use ONLY the information provided in the Raw Research Context to generate the report. Do not use outside knowledge.
3. Structure your final output clearly, addressing all 'sub_questions' from the brief.
4. If the data is insufficient for a sub-question, clearly state the gap based on the reflection log.
5. Your final output should be a plain text report, suitable for immediate viewing.
"""

    user_prompt = f"""
### RESEARCH BRIEF (The Plan) ###
{json.dumps(research_brief, indent=2)}

### RAW RESEARCH CONTEXT (The Data) ###
{search_context_str}

### REFLECTION LOG ###
{reflection_log}

Based on the plan and the context provided, generate the full final report now.
"""

    # 4. Call the LLM (Live Integration)
    try:
        # Assuming ollama_chat accepts system and user prompts and returns the text response
        raw_report = ollama_chat(system_prompt=system_prompt, user_prompt=user_prompt)
    except Exception as e:
        # Fallback if the LLM call fails
        raw_report = f"*** Synthesis Failed: Could not generate report. Error: {e} ***\n\nContext Provided:\n{search_context_str}"


    # 5. Update the state with the final result
    state["final_report"] = raw_report
    
    print("\n🎉 Synthesis complete. Final report generated.")
    return state