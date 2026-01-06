# # # # # # deep_research_graph.py

# # # # # from typing import Dict, Any, TypedDict, List, Optional
# # # # # from langgraph.graph import StateGraph, START, END
# # # # # import json

# # # # # # --- IMPORT ALL NODES ---
# # # # # from nodes.scoping import scoping_and_clarification
# # # # # from nodes.reseach_brief import build_research_brief
# # # # # from nodes.research import run_actual_research
# # # # # from nodes.reflection import run_reflection_tool
# # # # # from nodes.synthesis import run_synthesis # The final step!
# # # # # from dotenv import load_dotenv # <--- NEW IMPORT
# # # # # import os # <--- NEW IMPORT

# # # # # # --- ADD THIS LINE HERE ---
# # # # # # Load environment variables from the .env file immediately
# # # # # load_dotenv()
# # # # # # ============================================================
# # # # # # State Definition
# # # # # # ============================================================

# # # # # class ResearchState(TypedDict):
# # # # #     user_query: str
# # # # #     messages: List[Any]
# # # # #     scoping_result: Dict[str, Any]
# # # # #     next_node: Optional[str] 
# # # # #     research_brief: Optional[Dict[str, Any]]
# # # # #     clarification_depth: Optional[int]
    
# # # # #     # --- ADD THIS LINE ---
# # # # #     mission_id: Optional[int] 
    
# # # # #     # Research and Reflection Keys
# # # # #     raw_research_output: Optional[List[Dict[str, Any]]] 
# # # # #     reflection_log: Optional[str]        
# # # # #     is_data_sufficient: Optional[bool]
# # # # #     retry_count: Optional[int] # Add this to prevent infinite loops
    
# # # # #     # Final Output Key
# # # # #     final_report: Optional[str]


# # # # # # ============================================================
# # # # # # Graph Node Definitions
# # # # # # ============================================================

# # # # # def scoping_node(state: ResearchState) -> ResearchState:
# # # # #     """
# # # # #     Runs scoping + clarification logic.
# # # # #     Sets 'next_node' to 'research_brief' or 'clarification_needed'.
# # # # #     """
# # # # #     print("\n🌀 Running SCOPING node...")
# # # # #     updated_state, next_step = scoping_and_clarification(state)
# # # # #     updated_state["next_node"] = next_step
# # # # #     print(f"   -> Scoping complete. Decision: {next_step}")
# # # # #     return updated_state


# # # # # def research_brief_node(state: ResearchState) -> ResearchState:
# # # # #     """
# # # # #     Generates the research brief.
# # # # #     Unpacks the tuple from build_research_brief and sets the next step to 'research'.
# # # # #     """
# # # # #     print("\n📘 Generating Research Brief...\n")
# # # # #     updated_state, _ = build_research_brief(state)
# # # # #     updated_state["next_node"] = "research" 
# # # # #     return updated_state


# # # # # # ============================================================
# # # # # # Graph Builder
# # # # # # ============================================================

# # # # # def build_research_graph():
# # # # #     """Creates and compiles the LangGraph with the full agent pipeline."""
    
    
# # # # #     graph = StateGraph(ResearchState)

# # # # #     # 1. Register all nodes
# # # # #     graph.add_node("scoping", scoping_node)
# # # # #     graph.add_node("research_brief", research_brief_node)
# # # # #     graph.add_node("research", run_actual_research)
# # # # #     graph.add_node("reflection", run_reflection_tool)
# # # # #     graph.add_node("synthesis", run_synthesis)

# # # # #     # 2. Define Execution Flow (Edges)
# # # # #     graph.add_edge(START, "scoping")
    
# # # # #     # Conditional Edge from Scoping (Human-in-the-Loop)
# # # # #     graph.add_conditional_edges(
# # # # #         "scoping",
# # # # #         lambda state: state["next_node"],
# # # # #         {
# # # # #             "research_brief": "research_brief",  # Proceed to planning
# # # # #             "clarification_needed": END,         # Stop for user input
# # # # #         }
# # # # #     )
    
# # # # #     # Linear Flow: Planning -> Execution
# # # # #     graph.add_edge("research_brief", "research")

# # # # #     # Conditional Reflection Loop 
# # # # #     graph.add_edge("research", "reflection") # Search Execution -> Thinking Tool

# # # # #     graph.add_conditional_edges(
# # # # #         "reflection",
# # # # #         lambda state: state["next_node"],
# # # # #         {
# # # # #             "synthesis": "synthesis", # Proceed to final answer
# # # # #             "research": "research",   # Loop back and re-run research
# # # # #         }
# # # # #     )
    
# # # # #     # Final Edge
# # # # #     graph.add_edge("synthesis", END) 

# # # # #     return graph.compile()


# # # # # # ============================================================
# # # # # # Runner (User interaction loop)
# # # # # # ============================================================

# # # # # def run_deep_research():
# # # # #     print("\n🤖 Deep Research System Started\n")

# # # # #     user_query = input("🧑 Enter your research query: ")

# # # # #     initial_state = {
# # # # #         "user_query": user_query,
# # # # #         "messages": [],
# # # # #         "scoping_result": {},
# # # # #         "next_node": None,
# # # # #         "research_brief": None,
# # # # #         "clarification_depth": 0,
# # # # #         "mission_id": None,      # <--- Initialize
# # # # #         "retry_count": 0,       # <--- Initialize
# # # # #         "raw_research_output": None,
# # # # #         "reflection_log": None,
# # # # #         "is_data_sufficient": None,
# # # # #         "final_report": None
# # # # #     }

# # # # #     graph = build_research_graph()
# # # # #     current_state = initial_state
    
# # # # #     while True:
# # # # #         print("--- Invoking Graph ---")
        
# # # # #         # Invoke the graph with the current state
# # # # #         final_state = graph.invoke(current_state)
        
# # # # #         scoping_result = final_state.get("scoping_result", {})
        
# # # # #         # 1. Handle Clarification Loop (Human-in-the-Loop)
# # # # #         if final_state.get("next_node") == "clarification_needed":
            
# # # # #             question = scoping_result["clarification_question"]
            
# # # # #             print("\n===============================")
# # # # #             print("🛑 CLARIFICATION REQUIRED")
# # # # #             print("===============================")
# # # # #             print(f"AI: {question}")
            
# # # # #             clarification = input("\n🧑 Your Clarification: ")
            
# # # # #             # Update state for the next run
# # # # #             current_state = final_state
            
# # # # #             # The next scoping run will use the combined query history.
# # # # #             current_state["user_query"] = f"{current_state['user_query']} (Clarified: {clarification})"
            
# # # # #             # Clear previous results to force a clean restart of the scoping node
# # # # #             current_state["scoping_result"] = {} 
# # # # #             current_state["next_node"] = None
# # # # #             current_state["clarification_depth"] = current_state.get("clarification_depth", 0) + 1
            
# # # # #             continue # Loop restarts
            
# # # # #         else:
# # # # #             # 2. Final Output
# # # # #             final_report = final_state.get("final_report")
            
# # # # #             print("\n===============================")
# # # # #             print("🎉 FINAL RESEARCH REPORT")
# # # # #             print("===============================")

# # # # #             if final_report:
# # # # #                 print(f"\n{final_report}")
# # # # #             else:
# # # # #                 print("\nError: Final report was not generated by the Synthesis node.")
# # # # #                 print("\n--- Final State Trace ---")
# # # # #                 print(final_state.get("reflection_log", "No reflection log."))
# # # # #                 print("Brief:", final_state.get("research_brief", {}).get("summary", "N/A"))
            
# # # # #             break # Exit the loop


# # # # # if __name__ == "__main__":
# # # # #     run_deep_research()
# # # # # main.py

# # # # import os
# # # # import operator
# # # # from typing import Annotated, List, Union, Optional, Dict, Any, TypedDict
# # # # from langgraph.graph import StateGraph, START, END
# # # # from dotenv import load_dotenv

# # # # # --- IMPORT ALL NODES ---
# # # # from nodes.scoping import scoping_and_clarification
# # # # from nodes.reseach_brief import build_research_brief
# # # # from nodes.research import run_actual_research
# # # # from nodes.reflection import run_reflection_tool
# # # # from nodes.synthesis import run_synthesis
# # # # from langchain_core.tracers.langchain import wait_for_all_tracers
# # # # # Load environment variables
# # # # load_dotenv()

# # # # # ============================================================
# # # # # State Definition
# # # # # ============================================================

# # # # i

# # # # class ResearchState(TypedDict):
# # # #     # --- Input & Configuration ---
# # # #     user_query: str
# # # #     target: str # Extracted entity (e.g., "Goa")
# # # #     research_mode: Literal["fast", "deep"] # The "switch" for your agents
# # # #     active_domain: str # e.g., "travel" or "finance"
    
# # # #     # --- Flow Management ---
# # # #     messages: List[Any]
# # # #     next_node: Optional[str] 
# # # #     research_brief: Optional[Dict[str, Any]]
# # # #     clarification_depth: int # Initialize at 0
# # # #     mission_id: Optional[int] 
    
# # # #     # --- Research Data (The Collector) ---
# # # #     # Annotated[..., operator.add] is essential for Parallel Agents.
# # # #     # It allows multiple agents to add to this list simultaneously.
# # # #     raw_research_output: Annotated[List[Dict[str, Any]], operator.add] 
    
# # # #     # --- Reflection & Depth Logic ---
# # # #     reflection_log: Optional[str]        
# # # #     is_data_sufficient: bool # Used by the Deep agent to loop or exit
# # # #     retry_count: int
    
# # # #     # --- Final Output ---
# # # #     final_report: Optional[str]


# # # # # ============================================================
# # # # # Graph Node Wrappers
# # # # # ============================================================

# # # # def scoping_node(state: ResearchState) -> ResearchState:
# # # #     print("\n🌀 Running SCOPING node...")
# # # #     # The scoping_and_clarification function handles Postgres Mission creation
# # # #     updated_state, next_step = scoping_and_clarification(state)
# # # #     updated_state["next_node"] = next_step
# # # #     return updated_state

# # # # def research_brief_node(state: ResearchState) -> ResearchState:
# # # #     print("\n📘 Generating Research Brief...")
# # # #     # This function saves the tasks to the research_tasks table
# # # #     updated_state, _ = build_research_brief(state)
# # # #     updated_state["next_node"] = "research" 
# # # #     return updated_state

# # # # # ============================================================
# # # # # Graph Builder
# # # # # ============================================================

# # # # # ============================================================
# # # # # Graph Builder
# # # # # ============================================================

# # # # def build_research_graph():
# # # #     graph = StateGraph(ResearchState)

# # # #     graph.add_node("scoping", scoping_node)
# # # #     graph.add_node("research_brief", research_brief_node)
# # # #     graph.add_node("research", run_actual_research)
# # # #     graph.add_node("reflection", run_reflection_tool)
# # # #     graph.add_node("synthesis", run_synthesis)

# # # #     graph.add_edge(START, "scoping")
    
# # # #     graph.add_conditional_edges(
# # # #         "scoping",
# # # #         lambda state: state["next_node"],
# # # #         {
# # # #             "research_brief": "research_brief",
# # # #             "clarification_needed": END,
# # # #         }
# # # #     )
    
# # # #     graph.add_edge("research_brief", "research")
# # # #     graph.add_edge("research", "reflection")

# # # #     graph.add_conditional_edges(
# # # #         "reflection",
# # # #         lambda state: state["next_node"],
# # # #         {
# # # #             "synthesis": "synthesis",
# # # #             "research": "research",
# # # #         }
# # # #     )
    
# # # #     graph.add_edge("synthesis", END) 

# # # #     return graph.compile()

# # # # # --- CRITICAL: Define 'app' at the top level for Streamlit to find ---
# # # # app = build_research_graph()

# # # # # ============================================================
# # # # # Runner (User interaction loop for terminal)
# # # # # ============================================================

# # # # def run_deep_research():
# # # #     print("\n🤖 Deep Research System Initialized\n")
# # # #     user_query = input("🧑 Enter your research query: ")

# # # #     current_state: ResearchState = {
# # # #         "user_query": user_query,
# # # #         "messages": [],
# # # #         "scoping_result": {},
# # # #         "next_node": None,
# # # #         "research_brief": None,
# # # #         "clarification_depth": 0,
# # # #         "mission_id": None,
# # # #         "retry_count": 0,
# # # #         "raw_research_output": [],
# # # #         "reflection_log": "",
# # # #         "is_data_sufficient": False,
# # # #         "final_report": None
# # # #     }
    
# # # #     while True:
# # # #         print("\n--- Invoking Graph ---")
# # # #         # Use the globally defined 'app'
# # # #         final_state = app.invoke(current_state)
        
# # # #         scoping_result = final_state.get("scoping_result", {})
        
# # # #         if final_state.get("next_node") == "clarification_needed":
# # # #             question = scoping_result.get("clarification_question", "Clarification needed.")
# # # #             print(f"\nAI: {question}")
# # # #             user_input = input("\n🧑 Your Clarification: ")
            
# # # #             current_state = final_state
# # # #             current_state["user_query"] = f"{current_state['user_query']} (Clarified: {user_input})"
# # # #             current_state["scoping_result"] = {} 
# # # #             current_state["next_node"] = None
# # # #             continue 
            
# # # #         else:
# # # #             print(f"\n{final_state.get('final_report', 'No report generated.')}")
# # # #             break 
    
# # # #     wait_for_all_tracers()

# # # # if __name__ == "__main__":
# # # #     run_deep_research()
# # # import os
# # # import operator
# # # import asyncio
# # # from typing import Annotated, List, Union, Optional, Dict, Any, TypedDict, Literal
# # # from langgraph.graph import StateGraph, START, END
# # # from dotenv import load_dotenv

# # # # --- IMPORT ALL NODES ---
# # # from nodes.scoping import scoping_and_clarification
# # # from nodes.reseach_brief import build_research_brief
# # # # Ensure these two are exported/imported correctly from nodes/research.py
# # # from nodes.research import run_fast_research, run_deep_research 
# # # from nodes.reflection import run_reflection_tool
# # # from nodes.synthesis import run_synthesis
# # # from langchain_core.tracers.langchain import wait_for_all_tracers

# # # # Load environment variables
# # # load_dotenv()

# # # # ============================================================
# # # # State Definition
# # # # ============================================================

# # # class ResearchState(TypedDict):
# # #     # --- Input & Configuration ---
# # #     user_query: str
# # #     target: str 
# # #     research_mode: Literal["fast", "deep"] 
# # #     active_domain: str 
    
# # #     # --- Flow Management ---
# # #     messages: List[Any]
# # #     next_node: Optional[str] 
# # #     research_brief: Optional[Dict[str, Any]]
# # #     clarification_depth: int 
# # #     mission_id: Optional[int] 
    
# # #     # --- Research Data ---
# # #     # Annotated with operator.add allows parallel workers to merge results
# # #     raw_research_output: Annotated[List[Dict[str, Any]], operator.add] 
    
# # #     # --- Reflection & Depth Logic ---
# # #     reflection_log: Optional[str]        
# # #     is_data_sufficient: bool 
# # #     retry_count: int
    
# # #     # --- Final Output ---
# # #     final_report: Optional[str]

# # # # ============================================================
# # # # Router Logic
# # # # ============================================================
# # # def scoping_node(state: ResearchState) -> ResearchState:
# # #     print("\n🌀 Running SCOPING node...")
# # #     # Change: capture the tuple, but only return the state dict
# # #     updated_state, next_step = scoping_and_clarification(state)
    
# # #     # Store the next_step inside the state so the conditional edge can see it
# # #     updated_state["next_node"] = next_step
# # #     return updated_state # Return ONLY the dict

# # # def research_brief_node(state: ResearchState) -> ResearchState:
# # #     print("\n📘 Generating Research Brief...")
# # #     # Change: capture the tuple, but only return the state dict
# # #     updated_state, next_step = build_research_brief(state)
    
# # #     updated_state["next_node"] = next_step
# # #     return updated_state # Return ONLY the dict

# # # def research_mode_router(state: ResearchState):
# # #     """
# # #     Determines if the graph should follow the Fast (Parallel) 
# # #     or Deep (Sequential/Persistent) path.
# # #     """
# # #     mode = state.get("research_mode", "fast")
# # #     if mode == "deep":
# # #         return "deep_path"
# # #     return "fast_path"

# # # # ============================================================
# # # # Graph Builder
# # # # ============================================================

# # # def build_research_graph():
# # #     graph = StateGraph(ResearchState)

# # #     # 1. Register all nodes
# # #     graph.add_node("scoping", scoping_and_clarification)
# # #     graph.add_node("research_brief", build_research_brief)
    
# # #     # Path A: Fast Parallel (Direct memory results)
# # #     graph.add_node("fast_research", run_fast_research)
    
# # #     # Path B: Deep Sequential (Postgres persistent)
# # #     graph.add_node("deep_research", run_deep_research)
# # #     graph.add_node("reflection", run_reflection_tool)
    
# # #     # Final Step
# # #     graph.add_node("synthesis", run_synthesis)

# # #     # 2. Define Execution Flow
# # #     graph.add_edge(START, "scoping")
    
# # #     # Scoping Logic: Clarify or Plan
# # #     graph.add_conditional_edges(
# # #         "scoping",
# # #         lambda state: state["next_node"],
# # #         {
# # #             "research_brief": "research_brief",
# # #             "clarification_needed": END,
# # #         }
# # #     )
    
# # #     # Router: Fast vs Deep
# # #     graph.add_conditional_edges(
# # #         "research_brief",
# # #         research_mode_router,
# # #         {
# # #             "fast_path": "fast_research",
# # #             "deep_path": "deep_research"
# # #         }
# # #     )

# # #     # Fast Path Flow
# # #     graph.add_edge("fast_research", "synthesis")

# # #     # Deep Path Flow (with Reflection Loop)
# # #     graph.add_edge("deep_research", "reflection")
# # #     graph.add_conditional_edges(
# # #         "reflection",
# # #         lambda state: state["next_node"],
# # #         {
# # #             "synthesis": "synthesis",
# # #             "research": "deep_research",
# # #         }
# # #     )
    
# # #     graph.add_edge("synthesis", END) 

# # #     return graph.compile()

# # # app = build_research_graph()

# # # # ============================================================
# # # # Runner
# # # # ============================================================

# # # def run_research():
# # #     print("\n🤖 Multi-Agent Research System Initialized\n")
# # #     user_query = input("🧑 Enter your research query: ")

# # #     current_state: ResearchState = {
# # #         "user_query": user_query,
# # #         "target": "",
# # #         "research_mode": "fast", # Default, will be updated by scoping
# # #         "active_domain": "general",
# # #         "messages": [],
# # #         "next_node": None,
# # #         "research_brief": None,
# # #         "clarification_depth": 0,
# # #         "mission_id": None,
# # #         "retry_count": 0,
# # #         "raw_research_output": [],
# # #         "reflection_log": "",
# # #         "is_data_sufficient": False,
# # #         "final_report": None
# # #     }
    
# # #     # ... rest of your while loop remains the same ...
# # #     while True:
# # #         final_state = app.invoke(current_state)
# # #         # (Handling clarification and final report printing logic)
# # #         if final_state.get("next_node") == "clarification_needed":
# # #              # ... clarification logic ...
# # #              break
# # #         else:
# # #              print(f"\n{final_state.get('final_report')}")
# # #              break
# # #         wait_for_all_tracers()
# # # if __name__ == "__main__":
# # #     run_research()
# # import os
# # import operator
# # import asyncio
# # from typing import Annotated, List, Union, Optional, Dict, Any, TypedDict, Literal
# # from langgraph.graph import StateGraph, START, END
# # from dotenv import load_dotenv

# # # --- IMPORT ALL NODES ---
# # from nodes.scoping import scoping_and_clarification
# # from nodes.reseach_brief import build_research_brief
# # # Ensure these names match what is exported in your nodes/research.py
# # from nodes.research import run_fast_research, run_deep_research 
# # from nodes.reflection import run_reflection_tool
# # from nodes.synthesis import run_synthesis
# # from langchain_core.tracers.langchain import wait_for_all_tracers

# # # Load environment variables
# # load_dotenv()

# # # ============================================================
# # # State Definition
# # # ============================================================

# # class ResearchState(TypedDict):
# #     user_query: str
# #     target: str 
# #     research_mode: Literal["fast", "deep"] 
# #     active_domain: str 
# #     messages: List[Any]
# #     next_node: Optional[str] 
# #     research_brief: Optional[Dict[str, Any]]
# #     clarification_depth: int 
# #     mission_id: Optional[int] 
# #     raw_research_output: Annotated[List[Dict[str, Any]], operator.add] 
# #     reflection_log: Optional[str]        
# #     is_data_sufficient: bool 
# #     retry_count: int
# #     final_report: Optional[str]

# # # ============================================================
# # # Graph Node Wrappers (CRITICAL FIX)
# # # ============================================================

# # def scoping_node(state: ResearchState) -> ResearchState:
# #     """Wrapper to handle tuple return from scoping logic."""
# #     print("\n🌀 Running SCOPING node...")
# #     updated_state, next_step = scoping_and_clarification(state)
# #     updated_state["next_node"] = next_step # Unpack tuple into dict
# #     return updated_state # Return ONLY dict

# # def research_brief_node(state: ResearchState) -> ResearchState:
# #     """Wrapper to handle tuple return from brief logic."""
# #     print("\n📘 Generating Research Brief...")
# #     updated_state, next_step = build_research_brief(state)
# #     updated_state["next_node"] = next_step # Unpack tuple into dict
# #     return updated_state # Return ONLY dict

# # def research_mode_router(state: ResearchState):
# #     """Determines if path is Fast or Deep."""
# #     mode = state.get("research_mode", "fast")
# #     return "deep_path" if mode == "deep" else "fast_path"

# # # ============================================================
# # # Graph Builder
# # # ============================================================

# # def build_research_graph():
# #     graph = StateGraph(ResearchState)

# #     # 1. Register WRAPPERS, not raw functions
# #     graph.add_node("scoping", scoping_node)
# #     graph.add_node("research_brief", research_brief_node)
    
# #     graph.add_node("fast_research", run_fast_research)
# #     graph.add_node("deep_research", run_deep_research)
# #     graph.add_node("reflection", run_reflection_tool)
# #     graph.add_node("synthesis", run_synthesis)

# #     # 2. Define Execution Flow
# #     graph.add_edge(START, "scoping")
    
# #     graph.add_conditional_edges(
# #         "scoping",
# #         lambda state: state["next_node"],
# #         {
# #             "research_brief": "research_brief",
# #             "clarification_needed": END,
# #         }
# #     )
    
# #     graph.add_conditional_edges(
# #         "research_brief",
# #         research_mode_router,
# #         {
# #             "fast_path": "fast_research",
# #             "deep_path": "deep_research"
# #         }
# #     )

# #     graph.add_edge("fast_research", "synthesis")
# #     graph.add_edge("deep_research", "reflection")

# #     graph.add_conditional_edges(
# #         "reflection",
# #         lambda state: state["next_node"],
# #         {
# #             "synthesis": "synthesis",
# #             "research": "deep_research",
# #         }
# #     )
    
# #     graph.add_edge("synthesis", END) 

# #     return graph.compile()

# # app = build_research_graph()

# # # ============================================================
# # # Runner
# # # ============================================================

# # # ============================================================
# # # Runner (Updated for Async Support)
# # # ============================================================

# # async def run_research(): # 1. Make this function async
# #     print("\n🤖 Multi-Agent Research System Initialized\n")
# #     user_query = input("🧑 Enter your research query: ")

# #     current_state: ResearchState = {
# #         "user_query": user_query,
# #         "target": "",
# #         "research_mode": "fast",
# #         "active_domain": "general",
# #         "messages": [],
# #         "next_node": None,
# #         "research_brief": None,
# #         "clarification_depth": 0,
# #         "mission_id": None,
# #         "retry_count": 0,
# #         "raw_research_output": [],
# #         "reflection_log": "",
# #         "is_data_sufficient": False,
# #         "final_report": None
# #     }
    
# #     while True:
# #         print("\n--- Invoking Graph (Async) ---")
        
# #         # 2. Use ainvoke instead of invoke
# #         final_state = await app.ainvoke(current_state)
        
# #         if final_state.get("next_node") == "clarification_needed":
# #              scoping_res = final_state.get("scoping_result", {})
# #              question = scoping_res.get("clarification_question", "Need more info.")
# #              print(f"\nAI: {question}")
# #              user_input = input("\n🧑 Your Clarification: ")
             
# #              current_state = final_state
# #              current_state["user_query"] += f" (Clarification: {user_input})"
# #              current_state["next_node"] = None
# #              continue
# #         else:
# #              print("\n===============================")
# #              print("🎉 FINAL RESEARCH REPORT")
# #              print("===============================")
# #              print(final_state.get("final_report", "No report generated."))
# #              break
    
# #     wait_for_all_tracers()

# # if __name__ == "__main__":
# #     # 3. Use asyncio to run the entry point
# #     import asyncio
# #     asyncio.run(run_research())
# import asyncio
# import operator
# from typing import Annotated, List, Optional, Dict, Any, TypedDict, Literal
# from langgraph.graph import StateGraph, START, END
# import asyncio
# from nodes.scoping import scoping_and_clarification
# from nodes.reseach_brief import build_research_brief
# from nodes.research import run_fast_research, run_deep_research 
# from nodes.reflection import run_reflection_tool
# from nodes.synthesis import run_synthesis

# # 
# class ResearchState(TypedDict):
#     # Core Identity
#     user_query: str
#     user_id: int
#     mission_id: str 
    
#     # Logic Routing
#     target: Optional[str] 
#     research_mode: Literal["fast", "deep"] 
#     next_node: Optional[str] 
    
#     # Clarification Logic (The missing link)
#     clarification_needed: bool
#     clarification_question: Optional[str]
    
#     # Research Data
#     sub_questions: List[str]
#     # Annotated with operator.add so new research appends to old research
#     raw_research_output: Annotated[List[Dict[str, Any]], operator.add] 
#     final_report: Optional[str]

# # --- Wrappers ---
# def scoping_wrapper(state: ResearchState):
#     s, next_step = scoping_and_clarification(state)
#     s["next_node"] = next_step
#     return s

# def brief_wrapper(state: ResearchState) -> ResearchState:
#     print("\n📘 Generating Research Brief...")
#     # This calls your logic in nodes/research_brief.py
#     updated_state, next_step = build_research_brief(state)
    
#     # --- CRITICAL ADDITION ---
#     # Extract the actual questions from the brief for the research node to see
#     brief_data = updated_state.get("research_brief", {})
    
#     # Assuming your LLM returns a list of tasks in the brief JSON
#     tasks = brief_data.get("tasks", []) 
#     if not tasks and brief_data.get("sub_questions"):
#         tasks = brief_data.get("sub_questions")
        
#     updated_state["sub_questions"] = tasks 
#     # -------------------------
    
#     updated_state["next_node"] = "deep_research" 
#     return updated_state

# # --- Graph Builder ---
# def build_research_graph():
#     graph = StateGraph(ResearchState)

#     graph.add_node("scoping", scoping_wrapper)
#     graph.add_node("research_brief", brief_wrapper)
#     graph.add_node("fast_research", run_fast_research)
#     graph.add_node("deep_research", run_deep_research)
#     graph.add_node("reflection", run_reflection_tool)
#     graph.add_node("synthesis", run_synthesis)

#     graph.add_edge(START, "scoping")
    
#     # THE CRITICAL SWITCH
#     graph.add_conditional_edges(
#         "scoping",
#         lambda state: state["next_node"],
#         {
#             "research_brief": "research_brief", # Path for DEEP
#             "fast_research": "fast_research",   # Path for FAST (BYPASS BRIEF)
#             "clarification_needed": END,
#         }
#     )
    
#     graph.add_edge("research_brief", "deep_research")
#     graph.add_edge("fast_research", "synthesis")
#     graph.add_edge("deep_research", "reflection")

#     graph.add_conditional_edges(
#         "reflection",
#         lambda state: state["next_node"],
#         {
#             "synthesis": "synthesis",
#             "research": "deep_research",
#         }
#     )
    
#     graph.add_edge("synthesis", END) 
#     return graph.compile()
# app = build_research_graph()
# async def run_app():
#    # app = build_research_graph()
    
#     print("\n🚀 --- AI Deep Research System ---")
#     user_query = input("🧑 Enter your research topic: ")

#     # Initial State
#     current_state = {
#         "user_query": user_query,
#         "target": "",
#         "research_mode": "fast",
#         "messages": [],
#         "next_node": None,
#         "sub_questions": [],
#         "mission_id": None,
#         "retry_count": 0,
#         "raw_research_output": [],
#         "reflection_log": "",
#         "is_data_sufficient": False,
#         "final_report": None
        
#     }

#     while True:
#         print("\n⚙️  Processing...")
#         # Invoke the graph
#         final_state = await app.ainvoke(current_state)
        
#         # Check if we are in a Clarification Loop
#         if final_state.get("next_node") == "clarification_needed":
#             scoping_res = final_state.get("scoping_result", {})
#             question = scoping_res.get("clarification_question", "I need more details to provide a better result.")
            
#             print(f"\n❓ CLARIFICATION NEEDED: {question}")
#             user_answer = input("🧑 Your Response: ")
            
#             # Update state to re-run scoping with more context
#             current_state = final_state
#             current_state["user_query"] += f" (User Clarification: {user_answer})"
#             current_state["next_node"] = None 
#             continue # Restart the graph with the new information
            
#         else:
#             # Success Path
#             print("\n==================================================")
#             print("🎉 FINAL RESEARCH REPORT")
#             print("==================================================\n")
#             print(final_state.get("final_report", "Error: No report was generated."))
#             print("\n==================================================")
#             break

# if __name__ == "__main__":
    
#     try:
#         asyncio.run(run_app())
#     except KeyboardInterrupt:
#         print("\n👋 System exited by user.")
import asyncio
import operator
from typing import Annotated, List, Optional, Dict, Any, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver # <--- CRITICAL FOR STREAMLIT
from langchain_core.messages import trim_messages
# --- IMPORT ALL NODES ---
from nodes.scoping import scoping_and_clarification
from nodes.reseach_brief import build_research_brief
from nodes.research import run_fast_research, run_deep_research 
from nodes.reflection import run_reflection_tool
from nodes.synthesis import run_synthesis

# ============================================================
# 1. Unified State Definition
# ============================================================
class ResearchState(TypedDict):
    # Core Identity
    user_query: str
    original_query: str
    
    user_id: int
    mission_id: str 
    
    # Logic Routing
    target: Optional[str] 
    research_mode: Literal["fast", "deep"] 
    next_node: Optional[str] 
    
    # Clarification Logic (The link to app.py)
    clarification_needed: bool
    clarification_question: Optional[str]
    
    # Research Data
    sub_questions: List[str]
    # Annotated with operator.add so new research appends to existing research
    raw_research_output: Annotated[List[Dict[str, Any]], operator.add] 
    final_report: Optional[str]

# ============================================================
# 2. Node Wrappers (Ensuring Data is in the right keys)
# ============================================================


# def scoping_wrapper(state: ResearchState) -> ResearchState:
#     print("\n🌀 Running SCOPING node...")
#     # --- CONTEXT MERGING LOGIC ---
#     # If we already have a clarification question in state, it means 
#     # the current 'user_query' is an ANSWER to that question.
#     if state.get("clarification_needed") and state.get("clarification_question"):
#         previous_context = f"Original Query: {state['user_query']}\nAI Asked: {state['clarification_question']}"
#         # We don't overwrite user_query yet, we just pass the context 
#         # to the scoping function so the LLM can see the history.
#         state["user_query"] = f"{previous_context}\nUser Answered: {state['user_query']}"

#     # Run the underlying logic
#     updated_values, next_step = scoping_and_clarification(state)
    
#     # Flatten the results for the UI
#     if "scoping_result" in updated_values:
#         res = updated_values["scoping_result"]
#         updated_values["clarification_needed"] = res.get("clarification_needed", False)
#         updated_values["clarification_question"] = res.get("clarification_question")

#     updated_values["next_node"] = next_step
    # return updated_values
def scoping_wrapper(state: ResearchState) -> ResearchState:
    print("\n🌀 Running SCOPING node...")
    
    user_input = state.get("user_query", "")
    current_target = state.get("target", "").lower()
    
    # 1. Run scoping logic first to see what the NEW query is about
    updated_values, next_step = scoping_and_clarification(state)
    new_scoping = updated_values.get("scoping_result", {})
    new_target = new_scoping.get("target", "").lower()

    # 2. INTENT RESET: If the user changes location, clear the old "Memory"
    if current_target and new_target and current_target != new_target:
        print(f"🔄 Topic Switch Detected: {current_target} -> {new_target}. Resetting context.")
        state["original_query"] = user_input # Start fresh with the Mumbai query
        # Re-run once with the fresh context so it doesn't mention Genoa
        updated_values, next_step = scoping_and_clarification(state)

    # 3. FAST MODE BYPASS: If it's a simple question, don't use the "Trip Rule"
    if new_scoping.get("research_mode") == "fast":
        return {
            **updated_values,
            "clarification_needed": False, # Force false for fast facts
            "next_node": "fast_research"
        }

    return {
        **updated_values,
        "next_node": next_step
    }

def brief_wrapper(state: ResearchState) -> ResearchState:
    """Unpacks the research brief into tasks/sub-questions."""
    print("\n📘 Generating Research Brief...")
    updated_state, next_step = build_research_brief(state)
    
    # Extract tasks from the generated brief so research nodes can iterate over them
    brief_data = updated_state.get("research_brief", {})
    tasks = brief_data.get("tasks", []) or brief_data.get("sub_questions", [])
        
    updated_state["sub_questions"] = tasks 
    updated_state["next_node"] = "deep_research" 
    return updated_state

# ============================================================
# 3. Graph Builder
# ============================================================

def build_research_graph():
    # Initialize MemorySaver so the agent remembers previous clarifications
    memory = MemorySaver()
    
    graph = StateGraph(ResearchState)

    # Register Nodes
    graph.add_node("scoping", scoping_wrapper)
    graph.add_node("research_brief", brief_wrapper)
    graph.add_node("fast_research", run_fast_research)
    graph.add_node("deep_research", run_deep_research)
    graph.add_node("reflection", run_reflection_tool)
    graph.add_node("synthesis", run_synthesis)

    # Define Edges
    graph.add_edge(START, "scoping")
    
    graph.add_conditional_edges(
        "scoping",
        lambda state: state["next_node"],
        {
            "research_brief": "research_brief", 
            "fast_research": "fast_research",   
            "clarification_needed": END,         # Ends the run so Streamlit can take over
        }
    )
    
    graph.add_edge("research_brief", "deep_research")
    graph.add_edge("fast_research", "synthesis")
    graph.add_edge("deep_research", "reflection")

    graph.add_conditional_edges(
        "reflection",
        lambda state: state["next_node"],
        {
            "synthesis": "synthesis",
            "research": "deep_research",
        }
    )
    
    graph.add_edge("synthesis", END) 
    
    # Compile with checkpointer for persistence
    return graph.compile(checkpointer=memory)

# Export the app for app.py to import
app = build_research_graph()

# ============================================================
# 4. Terminal Runner (For local testing)
# ============================================================

async def run_terminal_app():
    print("\n🚀 --- AI Deep Research System (Terminal Mode) ---")
    user_query = input("🧑 Enter your research topic: ")
    
    # Use a fixed mission ID for the terminal session
    session_id = str(uuid.uuid4()) if 'uuid' in globals() else "terminal_test_id"

    current_state = {
        "user_query": user_query,
        "user_id": 1,
        "mission_id": session_id,
        "target": "",
        "research_mode": "fast",
        "sub_questions": [],
        "raw_research_output": [],
        "final_report": None,
        "clarification_needed": False,
        "clarification_question": None
    }

    config = {"configurable": {"thread_id": session_id}}

    while True:
        final_state = await app.ainvoke(current_state, config=config)
        
        if final_state.get("clarification_needed"):
            question = final_state.get("clarification_question", "Need more info.")
            print(f"\n❓ CLARIFICATION: {question}")
            user_answer = input("🧑 Your Response: ")
            
            # Update query and re-run
            current_state = final_state
            current_state["user_query"] += f" (Clarification: {user_answer})"
            continue 
        else:
            print("\n" + "="*50)
            print(final_state.get("final_report", "No report generated."))
            print("="*50 + "\n")
            break

if __name__ == "__main__":
    try:
        asyncio.run(run_terminal_app())
    except KeyboardInterrupt:
        print("\nExiting...")