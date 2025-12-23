import streamlit as st
import time
from main import app as graph_app 

st.set_page_config(page_title="Deep Research Agent", page_icon="🌀", layout="wide")

# Helper for the typewriter effect
def report_generator(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

st.title("🌀 Deep Research Agent")
st.markdown("---")

# 1. Sidebar
with st.sidebar:
    st.header("Mission Control")
    if st.button("Clear Session"):
        st.session_state.messages = []
        st.session_state.graph_state = {}
        st.rerun()

# 2. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. User Input
if prompt := st.chat_input("Where should we research next?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    inputs = {"user_query": prompt, "messages": [], "retry_count": 0, "clarification_depth": 0}

    with st.chat_message("assistant"):
        # 5. The Thinking / Progress Section
        with st.status("🚀 Launching Research Pipeline...", expanded=True) as status:
            final_state = {}
            
            # Stream graph updates to see intermediate steps
            for chunk in graph_app.stream(inputs, stream_mode="updates"):
                for node_name, output in chunk.items():
                    
                    if node_name == "scoping":
                        target = output.get("scoping_result", {}).get("target", "General")
                        st.write(f"🔍 **Scoping:** Identifying target as: *{target}*")
                    
                    elif node_name == "research_brief":
                        st.write("📋 **Briefing:** Drafting research plan and sub-questions.")
                    
                    elif node_name == "research":
                        # If your research node saves queries to state, show them here
                        queries = output.get("research_brief", {}).get("sub_questions", [])
                        if queries:
                            st.write(f"🌐 **Searching:** Executing {len(queries)} research queries...")
                            for q in queries:
                                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;*⤷ Searching for: {q}*")
                        else:
                            st.write("🌐 **Research:** Gathering data from the web.")
                    
                    elif node_name == "reflection":
                        is_suff = output.get("is_data_sufficient", False)
                        st.write(f"🤔 **Reflection:** Data sufficient? {'✅ Yes' if is_suff else '❌ No, refining...'}")
                    
                    elif node_name == "synthesis":
                        st.write("✍️ **Synthesis:** Creating the final report...")
                    
                    final_state.update(output)

            status.update(label="✅ Research Complete!", state="complete", expanded=False)

        # 6. Stream the final response
        scoping = final_state.get("scoping_result", {})
        if scoping.get("clarification_needed"):
            response = f"**Clarification Needed:** {scoping.get('clarification_question')}"
            st.markdown(response)
        else:
            report = final_state.get("final_report", "No report generated.")
            # Use Streamlit's typewriter streaming
            response = st.write_stream(report_generator(report))

        # Save to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.graph_state = final_state