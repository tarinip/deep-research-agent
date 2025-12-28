# import streamlit as st
# import time
# import uuid
# import io
# import asyncio
# from main import app as graph_app 
# from utils.auth_utils import (
#     register_user, 
#     authenticate_user, 
#     get_user_history, 
#     load_past_research,
#     save_final_report_to_db # New utility
# )

# st.set_page_config(page_title="Deep Research Agent", page_icon="🌀", layout="wide")

# # Helper for the typewriter effect
# def report_generator(text):
#     for word in text.split(" "):
#         yield word + " "
#         time.sleep(0.01)

# # --- AUTHENTICATION UI ---
# def auth_gate():
#     st.sidebar.title("🔐 Access Control")
#     choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
#     if choice == "Sign Up":
#         st.title("📝 Create Account")
#         new_user = st.text_input("Username")
#         new_email = st.text_input("Email")
#         new_pass = st.text_input("Password", type="password")
#         if st.button("Register"):
#             if register_user(new_user, new_email, new_pass):
#                 st.success("Registration successful! Please switch to Login.")
#             else:
#                 st.error("Username or Email already exists.")
#     else:
#         st.title("🔑 Login")
#         user = st.text_input("Username")
#         pw = st.text_input("Password", type="password")
#         if st.button("Login"):
#             uid = authenticate_user(user, pw)
#             if uid:
#                 st.session_state.logged_in = True
#                 st.session_state.user_id = uid
#                 st.rerun()
#             else:
#                 st.error("Invalid credentials.")

# # --- RESEARCH INTERFACE ---
# def research_interface():
#     with st.sidebar:
#         st.header(f"👤 User: {st.session_state.user_id}")
#         if st.button("Logout"):
#             st.session_state.logged_in = False
#             st.rerun()
        
#         st.markdown("---")
#         st.header("📜 Research History")
#         history = get_user_history(st.session_state.user_id)
#         for mission_id, query, created_at in history:
#             if st.button(f"📄 {query[:20]}...", key=str(mission_id)):
#                 report = load_past_research(mission_id)
#                 st.session_state.messages = [{"role": "assistant", "content": report}]
#                 st.session_state.current_report = report
#                 st.rerun()

#     st.title("🌀 Deep Research Agent")
    
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     if prompt := st.chat_input("Where should we research next?"):
#         current_mission_id = str(uuid.uuid4())
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         inputs = {
#             "user_query": prompt, 
#             "user_id": st.session_state.user_id,
#             "mission_id": current_mission_id,
#             "raw_research_output": []
#         }

#         with st.chat_message("assistant"):
#             with st.status("🚀 Launching Research Pipeline...", expanded=True) as status:
#                 final_state = {}
#                 for chunk in graph_app.stream(inputs, stream_mode="updates"):
#                     for node_name, output in chunk.items():
#                         final_state.update(output)
#                         if node_name == "scoping":
#                             st.write("🔍 **Scoping:** Analyzing parameters...")
#                         elif node_name == "research":
#                             st.write("🌐 **Research:** Gathering web data...")
#                         elif node_name == "synthesis":
#                             st.write("✍️ **Synthesis:** Finalizing report...")
                
#                 status.update(label="✅ Research Complete!", state="complete", expanded=False)

#             report = final_state.get("final_report", "No report generated.")
#             response = st.write_stream(report_generator(report))
            
#             # Save to Database for History
#             save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, response)
            
#             st.session_state.messages.append({"role": "assistant", "content": response})
#             st.session_state.current_report = response

#     # --- DOWNLOAD SECTION ---
#     if "current_report" in st.session_state and st.session_state.current_report:
#         st.markdown("---")
#         st.download_button(
#             label="📥 Download Research as Text",
#             data=st.session_state.current_report,
#             file_name=f"research_{st.session_state.user_id}.txt",
#             mime="text/plain"
#         )

# # --- ENTRY POINT ---
# if __name__ == "__main__":
#     if "logged_in" not in st.session_state:
#         st.session_state.logged_in = False

#     if not st.session_state.logged_in:
#         auth_gate()
#     else:
#         research_interface()
import streamlit as st
import time
import uuid
import asyncio
from main import app as graph_app 
from utils.auth_utils import (
    register_user, 
    authenticate_user, 
    get_user_history, 
    load_past_research,
    save_final_report_to_db
)

st.set_page_config(page_title="Deep Research Agent", page_icon="🌀", layout="wide")

# Helper for the typewriter effect
def report_generator(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

# --- ASYNC RUNNER FOR LANGGRAPH ---
async def run_research_graph(inputs):
    """Handles the async streaming from LangGraph and updates UI."""
    final_state = {}
    # Use astream because your nodes are 'async def'
    async for chunk in graph_app.astream(inputs, stream_mode="updates"):
        for node_name, output in chunk.items():
            final_state.update(output)
            # Live feedback in the UI
            if node_name == "scoping":
                st.info("🔍 **Scoping:** Analyzing parameters and mission target...")
            elif node_name == "research_brief":
                st.info("📋 **Briefing:** Generating research tracks...")
            elif node_name == "deep_research":
                st.info("🌐 **Deep Research:** Executing parallel search tasks...")
            elif node_name == "fast_research":
                st.info("⚡ **Fast Research:** Quick-scanning web data...")
            elif node_name == "synthesis":
                st.info("✍️ **Synthesis:** Finalizing report...")
    return final_state

# --- AUTHENTICATION UI ---
def auth_gate():
    st.sidebar.title("🔐 Access Control")
    choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
    if choice == "Sign Up":
        st.title("📝 Create Account")
        new_user = st.text_input("Username")
        new_email = st.text_input("Email")
        new_pass = st.text_input("Password", type="password")
        if st.button("Register"):
            if register_user(new_user, new_email, new_pass):
                st.success("Registration successful! Please switch to Login.")
            else:
                st.error("Username or Email already exists.")
    else:
        st.title("🔑 Login")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            uid = authenticate_user(user, pw)
            if uid:
                st.session_state.logged_in = True
                st.session_state.user_id = uid
                st.rerun()
            else:
                st.error("Invalid credentials.")

# --- RESEARCH INTERFACE ---
def research_interface():
    with st.sidebar:
        st.header(f"👤 User: {st.session_state.user_id}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.markdown("---")
        st.header("📜 Research History")
        history = get_user_history(st.session_state.user_id)
        for m_id, query, created_at in history:
            # key must be unique, using mission_id
            if st.button(f"📄 {query[:25]}...", key=str(m_id)):
                report = load_past_research(m_id)
                st.session_state.messages = [{"role": "assistant", "content": report}]
                st.session_state.current_report = report
                st.rerun()

    st.title("🌀 Deep Research Agent")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Where should we research next?"):
        # 1. Generate the UUID for this mission
        current_mission_id = str(uuid.uuid4())
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        inputs = {
            "user_query": prompt, 
            "user_id": st.session_state.user_id,
            "mission_id": current_mission_id, # UUID passed to Graph
            "raw_research_output": []
        }

        with st.chat_message("assistant"):
            with st.status("🚀 Launching Research Pipeline...", expanded=True) as status:
                # 2. Run the Async Graph using asyncio.run
                try:
                    final_state = asyncio.run(run_research_graph(inputs))
                    status.update(label="✅ Research Complete!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Error during research: {e}")
                    status.update(label="❌ Research Failed", state="error")
                    final_state = {}

            report = final_state.get("final_report", "No report generated.")
            
            # 3. Display with streaming effect
            response = st.write_stream(report_generator(report))
            
            # 4. Save to Database
            save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.current_report = response

    # --- DOWNLOAD SECTION ---
    if "current_report" in st.session_state and st.session_state.current_report:
        st.markdown("---")
        st.download_button(
            label="📥 Download Research as Text",
            data=st.session_state.current_report,
            file_name=f"research_report_{int(time.time())}.txt",
            mime="text/plain"
        )

# --- ENTRY POINT ---
if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        auth_gate()
    else:
        research_interface()