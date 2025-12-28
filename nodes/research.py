import asyncio
import os
import requests
import psycopg2
from typing import Dict, Any, List
from pgvector.psycopg2 import register_vector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage

# --- SHARED TOOLS ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

ResearchState = Dict[str, Any]

async def run_research_router(state: ResearchState) -> ResearchState:
    """Entry point to decide between Fast and Deep research."""
    mode = state.get("research_mode", "fast")
    if mode == "fast":
        return await run_fast_research(state)
    else:
        return run_deep_research(state)

# 🚀 AGENT 1: FAST PARALLEL RESEARCH (DuckDuckGo API)
async def run_fast_research(state: ResearchState) -> ResearchState:
    tasks = state.get("sub_questions", [])
    if not tasks:
        tasks = [state.get("user_query", "general research")]

    print(f"⚡ Fast Mode: Executing {len(tasks)} tasks in parallel via DDG...")

    async def quick_worker(question: str):
        try:
            # Direct API Call to DuckDuckGo
            url = "https://api.duckduckgo.com/"
            params = {"q": question, "format": "json", "no_redirect": "1"}
            
            # Using a synchronous request inside a thread for simplicity in this worker
            response = requests.get(url, params=params)
            data = response.json()
            
            context = data.get("AbstractText", "")
            if not context and data.get("RelatedTopics"):
                context = "\n".join([t.get("Text", "") for t in data["RelatedTopics"][:3] if "Text" in t])
            
            if not context:
                # Prompt LLM to use internal knowledge if DDG Instant Answer is empty
                res = await llm.ainvoke(f"Provide a quick factual summary for: {question}")
            else:
                res = await llm.ainvoke(f"Summarize this DDG info for {question}: {context}")
                
            return {
                "query": question, 
                "content": res.content, 
                "source": data.get("AbstractURL", "https://duckduckgo.com")
            }
        except Exception as e:
            return {"query": question, "error": str(e)}

    results = await asyncio.gather(*[quick_worker(t) for t in tasks])
    return {"raw_research_output": results, "next_node": "synthesis"}

# 🧐 AGENT 2: DEEP SEQUENTIAL RESEARCH (DuckDuckGo API + Postgres)
def run_deep_research(state: ResearchState) -> ResearchState:
    mission_id = state.get("mission_id")
    target = state.get("target", "the subject")
    
    if not mission_id:
        print("❌ No Mission ID found in state.")
        return state

    try:
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        register_vector(conn)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        return state

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

    for task_id, question in tasks:
        # A. Clean query for DDG
        query = question.replace("{target}", target)
        print(f"\n🔍 Deep Researching Task {task_id}: {query}")
        
        cur.execute("UPDATE research_tasks SET status = 'searching' WHERE id = %s", (task_id,))
        conn.commit()

        try:
            # B. DuckDuckGo Instant Answer API Call
            url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_redirect": "1"}
            response = requests.get(url, params=params)
            data = response.json()

            # C. Extract Context (Abstract or Related Topics)
            context = data.get("AbstractText", "")
            if not context and data.get("RelatedTopics"):
                context = "\n".join([t.get("Text", "") for t in data["RelatedTopics"][:3] if "Text" in t])

            # D. Summarize (Fallback to LLM knowledge if API returns nothing)
            if not context:
                print(f"      ⚠️ No DDG Instant Answer. Using LLM fallback...")
                summary_text = llm.invoke(f"Provide factual research on {query} regarding {target}").content
            else:
                summary_text = llm.invoke(f"Summarize this research context for {query}: {context}").content

            # E. Generate Embedding
            embedding = embeddings_model.embed_query(summary_text)

            # F. Save to Postgres
            source_url = data.get("AbstractURL") if data.get("AbstractURL") else "https://duckduckgo.com"
            cur.execute("""
                INSERT INTO research_nodes (mission_id, topic, content, source_url, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """, (mission_id, query, summary_text, source_url, embedding))

            # G. Update Task Status
            cur.execute(
                "UPDATE research_tasks SET status = 'completed', findings_summary = %s WHERE id = %s",
                (summary_text, task_id)
            )
            conn.commit()
            print(f"   ✅ Saved to Database (DDG API Powered)")

        except Exception as e:
            print(f"   ❌ Task {task_id} failed: {e}")
            cur.execute("UPDATE research_tasks SET status = 'failed' WHERE mission_id = %s", (task_id,))
            conn.commit()

    cur.close()
    conn.close()
    state["next_node"] = "reflection"
    return state