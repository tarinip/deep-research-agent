# deep_research_graph.py

from typing import Dict, Any, TypedDict, List, Optional
from langgraph.graph import StateGraph, START, END
import json

# --- IMPORT ALL NODES ---
from nodes.scoping import scoping_and_clarification
from nodes.reseach_brief import build_research_brief
from nodes.research import run_actual_research
from nodes.reflection import run_reflection_tool
from nodes.synthesis import run_synthesis # The final step!
from dotenv import load_dotenv # <--- NEW IMPORT
import os # <--- NEW IMPORT

# --- ADD THIS LINE HERE ---
# Load environment variables from the .env file immediately
load_dotenv()
# ============================================================
# State Definition
# ============================================================

class ResearchState(TypedDict):
    """
    Graph state structure. This defines all data passed between nodes.
    """
    user_query: str
    messages: List[Any]
    scoping_result: Dict[str, Any]
    next_node: Optional[str] 
    research_brief: Optional[Dict[str, Any]]
    clarification_depth: Optional[int]
    
    # Research and Reflection Keys
    raw_research_output: Optional[List[Dict[str, Any]]] 
    reflection_log: Optional[str]        
    is_data_sufficient: Optional[bool]
    
    # Final Output Key
    final_report: Optional[str]


# ============================================================
# Graph Node Definitions
# ============================================================

def scoping_node(state: ResearchState) -> ResearchState:
    """
    Runs scoping + clarification logic.
    Sets 'next_node' to 'research_brief' or 'clarification_needed'.
    """
    print("\n🌀 Running SCOPING node...")
    updated_state, next_step = scoping_and_clarification(state)
    updated_state["next_node"] = next_step
    print(f"   -> Scoping complete. Decision: {next_step}")
    return updated_state


def research_brief_node(state: ResearchState) -> ResearchState:
    """
    Generates the research brief.
    Unpacks the tuple from build_research_brief and sets the next step to 'research'.
    """
    print("\n📘 Generating Research Brief...\n")
    updated_state, _ = build_research_brief(state)
    updated_state["next_node"] = "research" 
    return updated_state


# ============================================================
# Graph Builder
# ============================================================

def build_research_graph():
    """Creates and compiles the LangGraph with the full agent pipeline."""
    
    
    graph = StateGraph(ResearchState)

    # 1. Register all nodes
    graph.add_node("scoping", scoping_node)
    graph.add_node("research_brief", research_brief_node)
    graph.add_node("research", run_actual_research)
    graph.add_node("reflection", run_reflection_tool)
    graph.add_node("synthesis", run_synthesis)

    # 2. Define Execution Flow (Edges)
    graph.add_edge(START, "scoping")
    
    # Conditional Edge from Scoping (Human-in-the-Loop)
    graph.add_conditional_edges(
        "scoping",
        lambda state: state["next_node"],
        {
            "research_brief": "research_brief",  # Proceed to planning
            "clarification_needed": END,         # Stop for user input
        }
    )
    
    # Linear Flow: Planning -> Execution
    graph.add_edge("research_brief", "research")

    # Conditional Reflection Loop 
    graph.add_edge("research", "reflection") # Search Execution -> Thinking Tool

    graph.add_conditional_edges(
        "reflection",
        lambda state: state["next_node"],
        {
            "synthesis": "synthesis", # Proceed to final answer
            "research": "research",   # Loop back and re-run research
        }
    )
    
    # Final Edge
    graph.add_edge("synthesis", END) 

    return graph.compile()


# ============================================================
# Runner (User interaction loop)
# ============================================================

def run_deep_research():
    print("\n🤖 Deep Research System Started\n")

    user_query = input("🧑 Enter your research query: ")

    initial_state = {
        "user_query": user_query,
        "messages": [],
        "scoping_result": {},
        "next_node": None,
        "research_brief": None,
        "clarification_depth": 0,
        "raw_research_output": None,
        "reflection_log": None,
        "is_data_sufficient": None,
        "final_report": None
    }

    graph = build_research_graph()
    current_state = initial_state
    
    while True:
        print("--- Invoking Graph ---")
        
        # Invoke the graph with the current state
        final_state = graph.invoke(current_state)
        
        scoping_result = final_state.get("scoping_result", {})
        
        # 1. Handle Clarification Loop (Human-in-the-Loop)
        if final_state.get("next_node") == "clarification_needed":
            
            question = scoping_result["clarification_question"]
            
            print("\n===============================")
            print("🛑 CLARIFICATION REQUIRED")
            print("===============================")
            print(f"AI: {question}")
            
            clarification = input("\n🧑 Your Clarification: ")
            
            # Update state for the next run
            current_state = final_state
            
            # The next scoping run will use the combined query history.
            current_state["user_query"] = f"{current_state['user_query']} (Clarified: {clarification})"
            
            # Clear previous results to force a clean restart of the scoping node
            current_state["scoping_result"] = {} 
            current_state["next_node"] = None
            current_state["clarification_depth"] = current_state.get("clarification_depth", 0) + 1
            
            continue # Loop restarts
            
        else:
            # 2. Final Output
            final_report = final_state.get("final_report")
            
            print("\n===============================")
            print("🎉 FINAL RESEARCH REPORT")
            print("===============================")

            if final_report:
                print(f"\n{final_report}")
            else:
                print("\nError: Final report was not generated by the Synthesis node.")
                print("\n--- Final State Trace ---")
                print(final_state.get("reflection_log", "No reflection log."))
                print("Brief:", final_state.get("research_brief", {}).get("summary", "N/A"))
            
            break # Exit the loop


if __name__ == "__main__":
    run_deep_research()