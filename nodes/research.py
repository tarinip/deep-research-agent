# # # nodes/research.py

# # import os
# # from typing import Dict, Any, List, Optional
# # import json
# # # Import the correct wrapper for SerpAPI
# # from langchain_community.utilities import SerpAPIWrapper 

# # # Assume ResearchState is defined/imported from the main file for type hinting
# # ResearchState = Dict[str, Any]


# # def run_actual_research(state: ResearchState) -> ResearchState:
# #     """
# #     Executes the search strategy defined in the research brief using SerpAPI.
# #     """
# #     print("\n🔍 Executing Research Node with SerpAPI...")

# #     # 1. Get the plan from the state
# #     research_brief = state.get("research_brief", {})
# #     sub_questions: List[str] = research_brief.get("sub_questions", [])
    
# #     if not sub_questions:
# #         print("⚠️ Warning: No sub-questions found in the brief. Aborting research.")
# #         state["raw_research_output"] = [{"error": "No sub-questions in brief."}]
# #         state["next_node"] = "synthesis" # Fallback to prevent immediate failure
# #         return state

# #     # 2. Initialize the Search Tool
# #     try:
# #         # SerpAPIWrapper automatically looks for the SERPAPI_API_KEY env var.
# #         # It runs the query and returns a raw dictionary result.
# #         search = SerpAPIWrapper(params={"engine": "google", "num": 5}) # num=5 for 5 results
# #     except Exception as e:
# #         error_msg = f"Error initializing SerpAPIWrapper. Check SERPAPI_API_KEY environment variable: {e}"
# #         print(f"Error: {error_msg}")
# #         state["raw_research_output"] = [{"error": error_msg}]
# #         state["next_node"] = "synthesis" 
# #         return state
    
# #     all_raw_results: List[Dict[str, Any]] = []

# #     # 3. Execute Searches for each sub-question
# #     print(f"   -> Running {len(sub_questions)} queries...")
# #     for i, question in enumerate(sub_questions):
# #         print(f"      -> Query {i+1}/{len(sub_questions)}: {question[:70]}...")
# #         try:
# #             # SerpAPIWrapper's results() method returns the raw JSON from SerpAPI.
# #             # This raw JSON typically includes organic results, knowledge graphs, etc.
# #             raw_json_result = search.results(question) 
# #             all_raw_results.append({
# #                 "query": question,
# #                 "raw_json_result": raw_json_result,
# #                 "status": "success"
# #             })
# #         except Exception as e:
# #             print(f"      -> Search failed for query '{question}': {e}")
# #             all_raw_results.append({"query": question, "raw_json_result": {}, "status": "failed", "error": str(e)})

# #     # 4. Update the state with raw results
# #     state["raw_research_output"] = all_raw_results
    
# #     # 5. Signal the next node: Reflection/Critique
# #     state["next_node"] = "reflection"

# #     print("\n✅ Research execution complete. Passing to Reflection tool.")
# #     return state
# # nodes/research.py

# # nodes/research.py

# import os
# from typing import Dict, Any, List
# from langchain_community.utilities import SerpAPIWrapper 

# ResearchState = Dict[str, Any]

# def run_actual_research(state: ResearchState) -> ResearchState:
#     """
#     Executes search strategy with a 'Smart Fallback' to prevent empty result loops.
#     """
#     print("\n🔍 Executing Research Node...")

#     # 1. Setup from state
#     research_brief = state.get("research_brief", {})
#     sub_questions: List[str] = research_brief.get("sub_questions", [])
#     settings = research_brief.get("settings", {})
    
#     max_results = settings.get("max_sources", 5)
#     priority_domains = settings.get("priority_sources", [])

#     if not sub_questions:
#         print("⚠️ No sub-questions found. Skipping.")
#         return state

#     # 2. Initialize SerpAPI
#     try:
#         search = SerpAPIWrapper(params={
#             "engine": "google", 
#             "num": max_results
#         })
#     except Exception as e:
#         print(f"❌ SerpAPI Init Error: {e}")
#         return state
    
#     all_findings = []

#     # 3. Execution Loop with Fallback Logic
#     for question in sub_questions:
#         # Step A: Attempt constrained search if priority domains exist
#         query = question
#         using_constraints = False
        
#         if priority_domains:
#             sites = " OR ".join([f"site:{d}" for d in priority_domains])
#             query = f"{question} ({sites})"
#             using_constraints = True

#         print(f"   -> Researching: {question[:60]}...")
        
#         try:
#             raw_data = search.results(query)
#             organic_results = raw_data.get("organic_results", [])

#             # Step B: Smart Fallback 
#             # If constrained search returned nothing, try a broad search immediately
#             if not organic_results and using_constraints:
#                 print(f"      ⚠️ No results found on priority sites. Retrying globally...")
#                 raw_data = search.results(question) # Original question without 'site:'
#                 organic_results = raw_data.get("organic_results", [])

#             # 4. Data Cleaning
#             clean_results = [
#                 {
#                     "title": r.get("title"),
#                     "link": r.get("link"),
#                     "snippet": r.get("snippet"),
#                     "source": r.get("source", "Web")
#                 } for r in organic_results
#             ]
            
#             # If still empty after fallback, add a 'No info' marker instead of an empty list
#             # This helps the Reflection node see that the attempt was made.
#             if not clean_results:
#                 clean_results = [{
#                     "title": "No results found",
#                     "link": "N/A",
#                     "snippet": f"Search for '{question}' yielded no results even after fallback."
#                 }]

#             all_findings.append({
#                 "query": question,
#                 "results": clean_results,
#                 "knowledge_graph": raw_data.get("knowledge_graph", {})
#             })
            
#         except Exception as e:
#             print(f"      ! Search failed: {e}")

#     # 5. Update State
#     state["raw_research_output"] = all_findings
#     state["next_node"] = "reflection"

#     print(f"✅ Research complete. Collected data for {len(all_findings)} topics.")
#     return state
import os
import psycopg2
from typing import Dict, Any, List
from langchain_community.utilities import SerpAPIWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
load_dotenv()
ResearchState = Dict[str, Any]

def run_actual_research(state: ResearchState) -> ResearchState:
    mission_id = state.get("mission_id")
    if not mission_id:
        print("❌ No Mission ID found in state.")
        return state

    # 1. Initialize OpenAI Tools (Requires OPENAI_API_KEY in env)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 2. Database Connection
    try:
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        register_vector(conn)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        return state

    # 3. Fetch pending tasks
    cur.execute(
        "SELECT id, question FROM research_tasks WHERE mission_id = %s AND status = 'pending'",
        (mission_id,)
    )
    tasks = cur.fetchall()

    if not tasks:
        print("✅ No pending tasks. Moving to synthesis.")
        state["next_node"] = "synthesis"
        cur.close()
        conn.close()
        return state

    search = SerpAPIWrapper()
    
    for task_id, question in tasks:
        print(f"\n🔍 Researching Task {task_id}: {question}")
        
        cur.execute("UPDATE research_tasks SET status = 'searching' WHERE id = %s", (task_id,))
        conn.commit()

        try:
            # A. Google Search
            raw_results = search.results(question)
            organic = raw_results.get("organic_results", [])[:3]
            context = "\n".join([f"{r.get('title')}: {r.get('snippet')}" for r in organic])

            if not context:
                raise ValueError("No search results found.")

            # B. Summarize with GPT-4o-mini
            summary_messages = [
                SystemMessage(content="You are a factual research assistant. Summarize the key facts concisely."),
                HumanMessage(content=f"Summarize these results for '{question}':\n\n{context}")
            ]
            # Use LangChain invoke
            response = llm.invoke(summary_messages)
            summary_text = response.content

            # C. Generate Embedding with OpenAI
            # This replaces the ollama.embeddings call
            embedding = embeddings_model.embed_query(summary_text)

            # D. Save to Postgres
            source_url = organic[0].get('link') if organic else 'N/A'
            cur.execute("""
                INSERT INTO research_nodes (mission_id, topic, content, source_url, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """, (mission_id, question, summary_text, source_url, embedding))

            # E. Update Task Status
            cur.execute(
                "UPDATE research_tasks SET status = 'completed', findings_summary = %s WHERE id = %s",
                (summary_text, task_id)
            )
            conn.commit()
            print(f"   ✅ Saved to Database (OpenAI Powered)")

        except Exception as e:
            print(f"   ❌ Task {task_id} failed: {e}")
            cur.execute("UPDATE research_tasks SET status = 'failed' WHERE id = %s", (task_id,))
            conn.commit()

    cur.close()
    conn.close()
    state["next_node"] = "reflection"
    return state