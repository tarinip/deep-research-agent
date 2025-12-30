# # # # # # # # import streamlit as st
# # # # # # # # import time
# # # # # # # # import uuid
# # # # # # # # import io
# # # # # # # # import asyncio
# # # # # # # # from main import app as graph_app 
# # # # # # # # from utils.auth_utils import (
# # # # # # # #     register_user, 
# # # # # # # #     authenticate_user, 
# # # # # # # #     get_user_history, 
# # # # # # # #     load_past_research,
# # # # # # # #     save_final_report_to_db # New utility
# # # # # # # # )

# # # # # # # # st.set_page_config(page_title="Deep Research Agent", page_icon="🌀", layout="wide")

# # # # # # # # # Helper for the typewriter effect
# # # # # # # # def report_generator(text):
# # # # # # # #     for word in text.split(" "):
# # # # # # # #         yield word + " "
# # # # # # # #         time.sleep(0.01)

# # # # # # # # # --- AUTHENTICATION UI ---
# # # # # # # # def auth_gate():
# # # # # # # #     st.sidebar.title("🔐 Access Control")
# # # # # # # #     choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
# # # # # # # #     if choice == "Sign Up":
# # # # # # # #         st.title("📝 Create Account")
# # # # # # # #         new_user = st.text_input("Username")
# # # # # # # #         new_email = st.text_input("Email")
# # # # # # # #         new_pass = st.text_input("Password", type="password")
# # # # # # # #         if st.button("Register"):
# # # # # # # #             if register_user(new_user, new_email, new_pass):
# # # # # # # #                 st.success("Registration successful! Please switch to Login.")
# # # # # # # #             else:
# # # # # # # #                 st.error("Username or Email already exists.")
# # # # # # # #     else:
# # # # # # # #         st.title("🔑 Login")
# # # # # # # #         user = st.text_input("Username")
# # # # # # # #         pw = st.text_input("Password", type="password")
# # # # # # # #         if st.button("Login"):
# # # # # # # #             uid = authenticate_user(user, pw)
# # # # # # # #             if uid:
# # # # # # # #                 st.session_state.logged_in = True
# # # # # # # #                 st.session_state.user_id = uid
# # # # # # # #                 st.rerun()
# # # # # # # #             else:
# # # # # # # #                 st.error("Invalid credentials.")

# # # # # # # # # --- RESEARCH INTERFACE ---
# # # # # # # # def research_interface():
# # # # # # # #     with st.sidebar:
# # # # # # # #         st.header(f"👤 User: {st.session_state.user_id}")
# # # # # # # #         if st.button("Logout"):
# # # # # # # #             st.session_state.logged_in = False
# # # # # # # #             st.rerun()
        
# # # # # # # #         st.markdown("---")
# # # # # # # #         st.header("📜 Research History")
# # # # # # # #         history = get_user_history(st.session_state.user_id)
# # # # # # # #         for mission_id, query, created_at in history:
# # # # # # # #             if st.button(f"📄 {query[:20]}...", key=str(mission_id)):
# # # # # # # #                 report = load_past_research(mission_id)
# # # # # # # #                 st.session_state.messages = [{"role": "assistant", "content": report}]
# # # # # # # #                 st.session_state.current_report = report
# # # # # # # #                 st.rerun()

# # # # # # # #     st.title("🌀 Deep Research Agent")
    
# # # # # # # #     if "messages" not in st.session_state:
# # # # # # # #         st.session_state.messages = []

# # # # # # # #     for message in st.session_state.messages:
# # # # # # # #         with st.chat_message(message["role"]):
# # # # # # # #             st.markdown(message["content"])

# # # # # # # #     if prompt := st.chat_input("Where should we research next?"):
# # # # # # # #         current_mission_id = str(uuid.uuid4())
# # # # # # # #         st.session_state.messages.append({"role": "user", "content": prompt})
        
# # # # # # # #         with st.chat_message("user"):
# # # # # # # #             st.markdown(prompt)

# # # # # # # #         inputs = {
# # # # # # # #             "user_query": prompt, 
# # # # # # # #             "user_id": st.session_state.user_id,
# # # # # # # #             "mission_id": current_mission_id,
# # # # # # # #             "raw_research_output": []
# # # # # # # #         }

# # # # # # # #         with st.chat_message("assistant"):
# # # # # # # #             with st.status("🚀 Launching Research Pipeline...", expanded=True) as status:
# # # # # # # #                 final_state = {}
# # # # # # # #                 for chunk in graph_app.stream(inputs, stream_mode="updates"):
# # # # # # # #                     for node_name, output in chunk.items():
# # # # # # # #                         final_state.update(output)
# # # # # # # #                         if node_name == "scoping":
# # # # # # # #                             st.write("🔍 **Scoping:** Analyzing parameters...")
# # # # # # # #                         elif node_name == "research":
# # # # # # # #                             st.write("🌐 **Research:** Gathering web data...")
# # # # # # # #                         elif node_name == "synthesis":
# # # # # # # #                             st.write("✍️ **Synthesis:** Finalizing report...")
                
# # # # # # # #                 status.update(label="✅ Research Complete!", state="complete", expanded=False)

# # # # # # # #             report = final_state.get("final_report", "No report generated.")
# # # # # # # #             response = st.write_stream(report_generator(report))
            
# # # # # # # #             # Save to Database for History
# # # # # # # #             save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, response)
            
# # # # # # # #             st.session_state.messages.append({"role": "assistant", "content": response})
# # # # # # # #             st.session_state.current_report = response

# # # # # # # #     # --- DOWNLOAD SECTION ---
# # # # # # # #     if "current_report" in st.session_state and st.session_state.current_report:
# # # # # # # #         st.markdown("---")
# # # # # # # #         st.download_button(
# # # # # # # #             label="📥 Download Research as Text",
# # # # # # # #             data=st.session_state.current_report,
# # # # # # # #             file_name=f"research_{st.session_state.user_id}.txt",
# # # # # # # #             mime="text/plain"
# # # # # # # #         )

# # # # # # # # # --- ENTRY POINT ---
# # # # # # # # if __name__ == "__main__":
# # # # # # # #     if "logged_in" not in st.session_state:
# # # # # # # #         st.session_state.logged_in = False

# # # # # # # #     if not st.session_state.logged_in:
# # # # # # # #         auth_gate()
# # # # # # # #     else:
# # # # # # # #         research_interface()
# # # # # # # import streamlit as st
# # # # # # # import time
# # # # # # # import uuid
# # # # # # # import asyncio
# # # # # # # from main import app as graph_app 
# # # # # # # from utils.auth_utils import (
# # # # # # #     register_user, 
# # # # # # #     authenticate_user, 
# # # # # # #     get_user_history, 
# # # # # # #     load_past_research,
# # # # # # #     save_final_report_to_db
# # # # # # # )

# # # # # # # st.set_page_config(page_title="Deep Research Agent", page_icon="🌀", layout="wide")

# # # # # # # # Helper for the typewriter effect
# # # # # # # def report_generator(text):
# # # # # # #     for word in text.split(" "):
# # # # # # #         yield word + " "
# # # # # # #         time.sleep(0.01)

# # # # # # # # --- ASYNC RUNNER FOR LANGGRAPH ---
# # # # # # # async def run_research_graph(inputs):
# # # # # # #     """Handles the async streaming from LangGraph and updates UI."""
# # # # # # #     final_state = {}
# # # # # # #     # Use astream because your nodes are 'async def'
# # # # # # #     async for chunk in graph_app.astream(inputs, stream_mode="updates"):
# # # # # # #         for node_name, output in chunk.items():
# # # # # # #             final_state.update(output)
# # # # # # #             # Live feedback in the UI
# # # # # # #             if node_name == "scoping":
# # # # # # #                 st.info("🔍 **Scoping:** Analyzing parameters and mission target...")
# # # # # # #             elif node_name == "research_brief":
# # # # # # #                 st.info("📋 **Briefing:** Generating research tracks...")
# # # # # # #             elif node_name == "deep_research":
# # # # # # #                 st.info("🌐 **Deep Research:** Executing parallel search tasks...")
# # # # # # #             elif node_name == "fast_research":
# # # # # # #                 st.info("⚡ **Fast Research:** Quick-scanning web data...")
# # # # # # #             elif node_name == "synthesis":
# # # # # # #                 st.info("✍️ **Synthesis:** Finalizing report...")
# # # # # # #     return final_state

# # # # # # # # --- AUTHENTICATION UI ---
# # # # # # # def auth_gate():
# # # # # # #     st.sidebar.title("🔐 Access Control")
# # # # # # #     choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
# # # # # # #     if choice == "Sign Up":
# # # # # # #         st.title("📝 Create Account")
# # # # # # #         new_user = st.text_input("Username")
# # # # # # #         new_email = st.text_input("Email")
# # # # # # #         new_pass = st.text_input("Password", type="password")
# # # # # # #         if st.button("Register"):
# # # # # # #             if register_user(new_user, new_email, new_pass):
# # # # # # #                 st.success("Registration successful! Please switch to Login.")
# # # # # # #             else:
# # # # # # #                 st.error("Username or Email already exists.")
# # # # # # #     else:
# # # # # # #         st.title("🔑 Login")
# # # # # # #         user = st.text_input("Username")
# # # # # # #         pw = st.text_input("Password", type="password")
# # # # # # #         if st.button("Login"):
# # # # # # #             uid = authenticate_user(user, pw)
# # # # # # #             if uid:
# # # # # # #                 st.session_state.logged_in = True
# # # # # # #                 st.session_state.user_id = uid
# # # # # # #                 st.rerun()
# # # # # # #             else:
# # # # # # #                 st.error("Invalid credentials.")

# # # # # # # # --- RESEARCH INTERFACE ---
# # # # # # # def research_interface():
# # # # # # #     with st.sidebar:
# # # # # # #         st.header(f"👤 User: {st.session_state.user_id}")
# # # # # # #         if st.button("Logout"):
# # # # # # #             st.session_state.logged_in = False
# # # # # # #             st.rerun()
        
# # # # # # #         st.markdown("---")
# # # # # # #         st.header("📜 Research History")
# # # # # # #         history = get_user_history(st.session_state.user_id)
# # # # # # #         for m_id, query, created_at in history:
# # # # # # #             # key must be unique, using mission_id
# # # # # # #             if st.button(f"📄 {query[:25]}...", key=str(m_id)):
# # # # # # #                 report = load_past_research(m_id)
# # # # # # #                 st.session_state.messages = [{"role": "assistant", "content": report}]
# # # # # # #                 st.session_state.current_report = report
# # # # # # #                 st.rerun()

# # # # # # #     st.title("🌀 Deep Research Agent")
    
# # # # # # #     if "messages" not in st.session_state:
# # # # # # #         st.session_state.messages = []

# # # # # # #     # Display chat history
# # # # # # #     for message in st.session_state.messages:
# # # # # # #         with st.chat_message(message["role"]):
# # # # # # #             st.markdown(message["content"])

# # # # # # #     if prompt := st.chat_input("Where should we research next?"):
# # # # # # #         # 1. Generate the UUID for this mission
# # # # # # #         current_mission_id = str(uuid.uuid4())
        
# # # # # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # # # # #         with st.chat_message("user"):
# # # # # # #             st.markdown(prompt)

# # # # # # #         inputs = {
# # # # # # #             "user_query": prompt, 
# # # # # # #             "user_id": st.session_state.user_id,
# # # # # # #             "mission_id": current_mission_id, # UUID passed to Graph
# # # # # # #             "raw_research_output": []
# # # # # # #         }

# # # # # # #         with st.chat_message("assistant"):
# # # # # # #             with st.status("🚀 Launching Research Pipeline...", expanded=True) as status:
# # # # # # #                 # 2. Run the Async Graph using asyncio.run
# # # # # # #                 try:
# # # # # # #                     final_state = asyncio.run(run_research_graph(inputs))
# # # # # # #                     status.update(label="✅ Research Complete!", state="complete", expanded=False)
# # # # # # #                 except Exception as e:
# # # # # # #                     st.error(f"Error during research: {e}")
# # # # # # #                     status.update(label="❌ Research Failed", state="error")
# # # # # # #                     final_state = {}

# # # # # # #             report = final_state.get("final_report", "No report generated.")
            
# # # # # # #             # 3. Display with streaming effect
# # # # # # #             response = st.write_stream(report_generator(report))
            
# # # # # # #             # 4. Save to Database
# # # # # # #             save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, response)
            
# # # # # # #             st.session_state.messages.append({"role": "assistant", "content": response})
# # # # # # #             st.session_state.current_report = response

# # # # # # #     # --- DOWNLOAD SECTION ---
# # # # # # #     if "current_report" in st.session_state and st.session_state.current_report:
# # # # # # #         st.markdown("---")
# # # # # # #         st.download_button(
# # # # # # #             label="📥 Download Research as Text",
# # # # # # #             data=st.session_state.current_report,
# # # # # # #             file_name=f"research_report_{int(time.time())}.txt",
# # # # # # #             mime="text/plain"
# # # # # # #         )

# # # # # # # # --- ENTRY POINT ---
# # # # # # # if __name__ == "__main__":
# # # # # # #     if "logged_in" not in st.session_state:
# # # # # # #         st.session_state.logged_in = False

# # # # # # #     if not st.session_state.logged_in:
# # # # # # #         auth_gate()
# # # # # # #     else:
# # # # # # #         research_interface()
# # # # # # import streamlit as st
# # # # # # import time
# # # # # # import uuid
# # # # # # import asyncio
# # # # # # from main import app as graph_app 
# # # # # # from utils.auth_utils import (
# # # # # #     register_user, 
# # # # # #     authenticate_user, 
# # # # # #     get_user_history, 
# # # # # #     load_past_research,
# # # # # #     save_final_report_to_db
# # # # # # )

# # # # # # st.set_page_config(page_title="Deep Research Agent", page_icon="🌀", layout="wide")

# # # # # # # Helper for the typewriter effect
# # # # # # def report_generator(text):
# # # # # #     for word in text.split(" "):
# # # # # #         yield word + " "
# # # # # #         time.sleep(0.01)

# # # # # # # --- ASYNC RUNNER FOR LANGGRAPH ---
# # # # # # async def run_research_graph(inputs):
# # # # # #     """Handles async streaming and captures the final state."""
# # # # # #     final_state = {}
# # # # # #     async for chunk in graph_app.astream(inputs, stream_mode="updates"):
# # # # # #         for node_name, output in chunk.items():
# # # # # #             final_state.update(output)
# # # # # #             # Dynamic UI feedback based on the node currently running
# # # # # #             if node_name == "scoping":
# # # # # #                 st.info("🔍 **Scoping:** Analyzing your request for clarity...")
# # # # # #             elif node_name == "research_brief":
# # # # # #                 st.info("📋 **Briefing:** Planning research tracks...")
# # # # # #             elif node_name == "deep_research":
# # # # # #                 st.info("🌐 **Deep Research:** Gathering data from the web...")
# # # # # #             elif node_name == "synthesis":
# # # # # #                 st.info("✍️ **Synthesis:** Creating your travel guide...")
# # # # # #     return final_state

# # # # # # # --- AUTHENTICATION UI ---
# # # # # # def auth_gate():
# # # # # #     st.sidebar.title("🔐 Access Control")
# # # # # #     choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
# # # # # #     if choice == "Sign Up":
# # # # # #         st.title("📝 Create Account")
# # # # # #         new_user = st.text_input("Username")
# # # # # #         new_email = st.text_input("Email")
# # # # # #         new_pass = st.text_input("Password", type="password")
# # # # # #         if st.button("Register"):
# # # # # #             if register_user(new_user, new_email, new_pass):
# # # # # #                 st.success("Registration successful! Please switch to Login.")
# # # # # #             else:
# # # # # #                 st.error("Username or Email already exists.")
# # # # # #     else:
# # # # # #         st.title("🔑 Login")
# # # # # #         user = st.text_input("Username")
# # # # # #         pw = st.text_input("Password", type="password")
# # # # # #         if st.button("Login"):
# # # # # #             uid = authenticate_user(user, pw)
# # # # # #             if uid:
# # # # # #                 st.session_state.logged_in = True
# # # # # #                 st.session_state.user_id = uid
# # # # # #                 st.rerun()
# # # # # #             else:
# # # # # #                 st.error("Invalid credentials.")

# # # # # # # --- RESEARCH INTERFACE ---
# # # # # # def research_interface():
# # # # # #     with st.sidebar:
# # # # # #         st.header(f"👤 User: {st.session_state.user_id}")
# # # # # #         if st.button("Logout"):
# # # # # #             st.session_state.logged_in = False
# # # # # #             st.rerun()
        
# # # # # #         st.markdown("---")
# # # # # #         st.header("📜 Research History")
# # # # # #         history = get_user_history(st.session_state.user_id)
# # # # # #         for m_id, query, created_at in history:
# # # # # #             if st.button(f"📄 {query[:25]}...", key=str(m_id)):
# # # # # #                 report = load_past_research(m_id)
# # # # # #                 st.session_state.messages = [{"role": "assistant", "content": report}]
# # # # # #                 st.session_state.current_report = report
# # # # # #                 st.rerun()

# # # # # #     st.title("🌀 Deep Research Agent")
    
# # # # # #     if "messages" not in st.session_state:
# # # # # #         st.session_state.messages = []

# # # # # #     # Display chat history
# # # # # #     for message in st.session_state.messages:
# # # # # #         with st.chat_message(message["role"]):
# # # # # #             st.markdown(message["content"])

# # # # # #     if prompt := st.chat_input("Ex: Plan a 3-day budget trip to Goa..."):
# # # # # #         current_mission_id = str(uuid.uuid4())
        
# # # # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # # # #         with st.chat_message("user"):
# # # # # #             st.markdown(prompt)

# # # # # #         inputs = {
# # # # # #             "user_query": prompt, 
# # # # # #             "user_id": st.session_state.user_id,
# # # # # #             "mission_id": current_mission_id,
# # # # # #             "raw_research_output": []
# # # # # #         }

# # # # # #         with st.chat_message("assistant"):
# # # # # #             with st.status("🚀 Processing...", expanded=True) as status:
# # # # # #                 try:
# # # # # #                     # Run the graph
# # # # # #                     final_state = asyncio.run(run_research_graph(inputs))
                    
# # # # # #                     # CHECK FOR CLARIFICATION
# # # # # #                     question = final_state.get("clarification_question")
# # # # # #                     report = final_state.get("final_report")

# # # # # #                     if question:
# # # # # #                         status.update(label="🤔 Info Needed", state="complete", expanded=False)
# # # # # #                         st.markdown(f"### I need a bit more info:\n{question}")
# # # # # #                         st.session_state.messages.append({"role": "assistant", "content": question})
# # # # # #                     elif report:
# # # # # #                         status.update(label="✅ Research Complete!", state="complete", expanded=False)
# # # # # #                         # Display report with typewriter effect
# # # # # #                         response = st.write_stream(report_generator(report))
# # # # # #                         # Save successful report
# # # # # #                         save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, response)
# # # # # #                         st.session_state.messages.append({"role": "assistant", "content": response})
# # # # # #                         st.session_state.current_report = response
# # # # # #                     else:
# # # # # #                         status.update(label="⚠️ No output generated", state="error")
                        
# # # # # #                 except Exception as e:
# # # # # #                     st.error(f"Error: {e}")
# # # # # #                     status.update(label="❌ Pipeline Failed", state="error")

# # # # # #     # --- DOWNLOAD SECTION ---
# # # # # #     if "current_report" in st.session_state and st.session_state.current_report:
# # # # # #         st.markdown("---")
# # # # # #         st.download_button(
# # # # # #             label="📥 Download Report",
# # # # # #             data=st.session_state.current_report,
# # # # # #             file_name=f"research_{int(time.time())}.txt",
# # # # # #             mime="text/plain"
# # # # # #         )

# # # # # # if __name__ == "__main__":
# # # # # #     if "logged_in" not in st.session_state:
# # # # # #         st.session_state.logged_in = False
# # # # # #     if not st.session_state.logged_in:
# # # # # #         auth_gate()
# # # # # #     else:
# # # # # #         research_interface()
# # # # # import streamlit as st
# # # # # import time
# # # # # import uuid
# # # # # import asyncio
# # # # # import io
# # # # # from main import app as graph_app 
# # # # # from utils.auth_utils import (
# # # # #     register_user, 
# # # # #     authenticate_user, 
# # # # #     get_user_history, 
# # # # #     load_past_research,
# # # # #     save_final_report_to_db
# # # # # )

# # # # # # --- PAGE CONFIG ---
# # # # # st.set_page_config(
# # # # #     page_title="Deep Travel Research Agent", 
# # # # #     page_icon="🌀", 
# # # # #     layout="wide"
# # # # # )

# # # # # # Helper for the typewriter effect
# # # # # def report_generator(text):
# # # # #     for word in text.split(" "):
# # # # #         yield word + " "
# # # # #         time.sleep(0.01)

# # # # # # --- ASYNC RUNNER FOR LANGGRAPH ---
# # # # # # async def run_research_graph(inputs):
# # # # # #     """
# # # # # #     Handles the async execution of the LangGraph.
# # # # # #     This allows 'async def' nodes like fast_research to run properly.
# # # # # #     """
# # # # # #     final_state = {}
# # # # # #     async for chunk in graph_app.astream(inputs, stream_mode="updates"):
# # # # # #         for node_name, output in chunk.items():
# # # # # #             final_state.update(output)
# # # # # #             # Live UI Status Updates
# # # # # #             if node_name == "scoping":
# # # # # #                 st.info("🔍 **Scoping:** Analyzing travel parameters...")
# # # # # #             elif node_name == "research_brief":
# # # # # #                 st.info("📋 **Briefing:** Creating specialized research tracks...")
# # # # # #             elif node_name == "deep_research":
# # # # # #                 st.info("🌐 **Deep Research:** Searching for real-time travel data...")
# # # # # #             elif node_name == "synthesis":
# # # # # #                 st.info("✍️ **Synthesis:** Finalizing your custom itinerary...")
# # # # # #     return final_state
# # # # # async def run_research_graph(inputs):
# # # # #     """Handles async streaming and ensures the FULL state is captured."""
# # # # #     final_state = {}
    
# # # # #     # We use astream to catch updates as they happen
# # # # #     async for chunk in graph_app.astream(inputs, stream_mode="updates"):
# # # # #         for node_name, output in chunk.items():
# # # # #             # This merges the node's output into our local final_state
# # # # #             final_state.update(output)
            
# # # # #             # LIVE UI FEEDBACK
# # # # #             if node_name == "scoping":
# # # # #                 # Check if scoping just produced a question
# # # # #                 if "clarification_question" in output and output["clarification_question"]:
# # # # #                     st.warning("🤔 Scoping identified missing details...")
# # # # #                 else:
# # # # #                     st.info("🔍 **Scoping:** Parameters verified.")
# # # # #             elif node_name == "research_brief":
# # # # #                 st.info("📋 **Briefing:** Research tracks created.")
# # # # #             # ... add other nodes as needed ...

# # # # #     return final_state
# # # # # # --- AUTHENTICATION UI ---
# # # # # def auth_gate():
# # # # #     st.sidebar.title("🔐 Access Control")
# # # # #     choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
# # # # #     if choice == "Sign Up":
# # # # #         st.title("📝 Create Account")
# # # # #         new_user = st.text_input("Username")
# # # # #         new_email = st.text_input("Email")
# # # # #         new_pass = st.text_input("Password", type="password")
# # # # #         if st.button("Register"):
# # # # #             if register_user(new_user, new_email, new_pass):
# # # # #                 st.success("Registration successful! Please switch to Login.")
# # # # #             else:
# # # # #                 st.error("Username or Email already exists.")
# # # # #     else:
# # # # #         st.title("🔑 Login")
# # # # #         user = st.text_input("Username")
# # # # #         pw = st.text_input("Password", type="password")
# # # # #         if st.button("Login"):
# # # # #             uid = authenticate_user(user, pw)
# # # # #             if uid:
# # # # #                 st.session_state.logged_in = True
# # # # #                 st.session_state.user_id = uid
# # # # #                 st.rerun()
# # # # #             else:
# # # # #                 st.error("Invalid credentials.")

# # # # # # --- RESEARCH INTERFACE ---
# # # # # def research_interface():
# # # # #     # Sidebar: User info and History
# # # # #     with st.sidebar:
# # # # #         st.header(f"👤 User: {st.session_state.user_id}")
# # # # #         if st.button("Logout"):
# # # # #             st.session_state.logged_in = False
# # # # #             st.rerun()
        
# # # # #         st.markdown("---")
# # # # #         st.header("📜 Research History")
# # # # #         history = get_user_history(st.session_state.user_id)
# # # # #         if history:
# # # # #             for m_id, query, created_at in history:
# # # # #                 # Use mission_id (UUID) as the key to prevent overlap
# # # # #                 if st.button(f"📄 {query[:25]}...", key=str(m_id)):
# # # # #                     report = load_past_research(m_id)
# # # # #                     st.session_state.messages = [{"role": "assistant", "content": report}]
# # # # #                     st.session_state.current_report = report
# # # # #                     st.rerun()
# # # # #         else:
# # # # #             st.caption("No past research found.")

# # # # #     st.title("🌀 Deep Travel Research Agent")
# # # # #     st.caption("Provide a destination and preferences for a detailed research-backed plan.")
    
# # # # #     # Chat History Display
# # # # #     if "messages" not in st.session_state:
# # # # #         st.session_state.messages = []

# # # # #     for message in st.session_state.messages:
# # # # #         with st.chat_message(message["role"]):
# # # # #             st.markdown(message["content"])

# # # # #     # Chat Input
# # # # #     if prompt := st.chat_input("Ex: Plan a 4-day heritage trip to Jaipur on a mid-range budget."):
# # # # #         # Generate new UUID for this specific mission
# # # # #         current_mission_id = str(uuid.uuid4())
        
# # # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # # #         with st.chat_message("user"):
# # # # #             st.markdown(prompt)

# # # # #         inputs = {
# # # # #             "user_query": prompt, 
# # # # #             "user_id": st.session_state.user_id,
# # # # #             "mission_id": current_mission_id,
# # # # #             "raw_research_output": []
# # # # #         }

# # # # #         with st.chat_message("assistant"):
# # # # #             with st.status("🚀 Processing Research Pipeline...", expanded=True) as status:
# # # # #                 try:
# # # # #                     # Run the Async Graph using asyncio.run to bridge with Streamlit Sync
# # # # #                     final_state = asyncio.run(run_research_graph(inputs))
                    
# # # # #                     # 1. CHECK FOR CLARIFICATION (Scoping Node result)
# # # # #                     question = final_state.get("clarification_question")
# # # # #                     report = final_state.get("final_report")

# # # # #                     if question:
# # # # #                         status.update(label="🤔 Clarification Required", state="complete", expanded=False)
# # # # #                         st.markdown("### ❓ I need more information")
# # # # #                         st.warning(question) # High visibility yellow box
# # # # #                         st.session_state.messages.append({"role": "assistant", "content": f"CLARIFICATION NEEDED: {question}"})
# # # # #                         final_state['final_report'] = None # Ensure we don't try to save a blank report
                    
# # # # #                     # 2. CHECK FOR COMPLETED REPORT
# # # # #                     elif report:
# # # # #                         status.update(label="✅ Research Complete!", state="complete", expanded=False)
# # # # #                         response = st.write_stream(report_generator(report))
                        
# # # # #                         # Save to Database (UUID compatible)
# # # # #                         save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, response)
                        
# # # # #                         st.session_state.messages.append({"role": "assistant", "content": response})
# # # # #                         st.session_state.current_report = response
                    
# # # # #                     else:
# # # # #                         status.update(label="⚠️ No response generated", state="error")

# # # # #                 except Exception as e:
# # # # #                     st.error(f"❌ Pipeline Error: {e}")
# # # # #                     status.update(label="Pipeline Failed", state="error")

# # # # #     # --- DOWNLOAD SECTION ---
# # # # #     if "current_report" in st.session_state and st.session_state.current_report:
# # # # #         st.markdown("---")
# # # # #         st.download_button(
# # # # #             label="📥 Download Research as Text",
# # # # #             data=st.session_state.current_report,
# # # # #             file_name=f"travel_research_{st.session_state.user_id}.txt",
# # # # #             mime="text/plain"
# # # # #         )

# # # # # # --- ENTRY POINT ---
# # # # # if __name__ == "__main__":
# # # # #     if "logged_in" not in st.session_state:
# # # # #         st.session_state.logged_in = False

# # # # #     if not st.session_state.logged_in:
# # # # #         auth_gate()
# # # # #     else:
# # # # #         research_interface()
# # # # import streamlit as st
# # # # import time
# # # # import uuid
# # # # import asyncio
# # # # from main import app as graph_app 
# # # # from utils.auth_utils import (
# # # #     register_user, 
# # # #     authenticate_user, 
# # # #     get_user_history, 
# # # #     load_past_research,
# # # #     save_final_report_to_db
# # # # )

# # # # # --- PAGE CONFIG ---
# # # # st.set_page_config(
# # # #     page_title="Deep Travel Research Agent", 
# # # #     page_icon="🌀", 
# # # #     layout="wide"
# # # # )

# # # # # Helper for the typewriter effect
# # # # def report_generator(text):
# # # #     for word in text.split(" "):
# # # #         yield word + " "
# # # #         time.sleep(0.01)

# # # # # --- ASYNC RUNNER FOR LANGGRAPH ---
# # # # async def run_research_graph(inputs):
# # # #     """Handles async streaming and ensures the FULL accumulated state is captured."""
# # # #     # We initialize with inputs to ensure user_id/mission_id are present
# # # #     final_state = dict(inputs) 
    
# # # #     async for chunk in graph_app.astream(inputs, stream_mode="updates"):
# # # #         for node_name, output in chunk.items():
# # # #             # Merging node output into our persistent state dictionary
# # # #             final_state.update(output)
            
# # # #             # --- PROGRESS FEEDBACK ---
# # # #             if node_name == "scoping":
# # # #                 if output.get("clarification_needed"):
# # # #                     st.toast("🤔 Scoping needs more info...", icon="❓")
# # # #                 else:
# # # #                     st.info("🔍 **Scoping:** Parameters verified.")
# # # #             elif node_name == "research_brief":
# # # #                 st.info("📋 **Briefing:** Research tracks created.")
# # # #             elif node_name == "deep_research":
# # # #                 st.info("🌐 **Deep Research:** Gathering data...")
# # # #             elif node_name == "synthesis":
# # # #                 st.info("✍️ **Synthesis:** Finalizing report...")

# # # #     # Return the full state which now includes 'clarification_question' OR 'final_report'
# # # #     return final_state

# # # # # --- AUTHENTICATION UI ---
# # # # def auth_gate():
# # # #     st.sidebar.title("🔐 Access Control")
# # # #     choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
# # # #     if choice == "Sign Up":
# # # #         st.title("📝 Create Account")
# # # #         new_user = st.text_input("Username")
# # # #         new_email = st.text_input("Email")
# # # #         new_pass = st.text_input("Password", type="password")
# # # #         if st.button("Register"):
# # # #             if register_user(new_user, new_email, new_pass):
# # # #                 st.success("Registration successful! Please switch to Login.")
# # # #             else:
# # # #                 st.error("Username or Email already exists.")
# # # #     else:
# # # #         st.title("🔑 Login")
# # # #         user = st.text_input("Username")
# # # #         pw = st.text_input("Password", type="password")
# # # #         if st.button("Login"):
# # # #             uid = authenticate_user(user, pw)
# # # #             if uid:
# # # #                 st.session_state.logged_in = True
# # # #                 st.session_state.user_id = uid
# # # #                 st.rerun()
# # # #             else:
# # # #                 st.error("Invalid credentials.")

# # # # # --- RESEARCH INTERFACE ---
# # # # def research_interface():
# # # #     with st.sidebar:
# # # #         st.header(f"👤 User: {st.session_state.user_id}")
# # # #         if st.button("Logout"):
# # # #             st.session_state.logged_in = False
# # # #             st.rerun()
        
# # # #         st.markdown("---")
# # # #         st.header("📜 Research History")
# # # #         history = get_user_history(st.session_state.user_id)
# # # #         if history:
# # # #             for m_id, query, created_at in history:
# # # #                 if st.button(f"📄 {query[:25]}...", key=str(m_id)):
# # # #                     report = load_past_research(m_id)
# # # #                     st.session_state.messages = [{"role": "assistant", "content": report}]
# # # #                     st.session_state.current_report = report
# # # #                     st.rerun()

# # # #     st.title("🌀 Deep Travel Research Agent")
    
# # # #     if "messages" not in st.session_state:
# # # #         st.session_state.messages = []

# # # #     for message in st.session_state.messages:
# # # #         with st.chat_message(message["role"]):
# # # #             st.markdown(message["content"])

# # # #     if prompt := st.chat_input("Ex: Plan a family trip to Orlando..."):
# # # #         current_mission_id = str(uuid.uuid4())
# # # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # # #         with st.chat_message("user"):
# # # #             st.markdown(prompt)

# # # #         inputs = {
# # # #             "user_query": prompt, 
# # # #             "user_id": st.session_state.user_id,
# # # #             "mission_id": current_mission_id,
# # # #             "raw_research_output": []
# # # #         }

# # # #         with st.chat_message("assistant"):
# # # #             with st.status("🚀 Processing Research...", expanded=True) as status:
# # # #                 try:
# # # #                     final_state = asyncio.run(run_research_graph(inputs))
                    
# # # #                     # UPDATED LOGIC TO MATCH LANGSMITH KEYS
# # # #                     needs_clarification = final_state.get("clarification_needed", False)
# # # #                     question = final_state.get("clarification_question")
# # # #                     report = final_state.get("final_report")

# # # #                     if needs_clarification and question:
# # # #                         status.update(label="🤔 Information Required", state="complete", expanded=False)
# # # #                         st.markdown("### ❓ I need more details")
# # # #                         st.warning(question) 
# # # #                         st.session_state.messages.append({"role": "assistant", "content": f"**Clarification Required:** {question}"})
                    
# # # #                     elif report:
# # # #                         status.update(label="✅ Research Complete!", state="complete", expanded=False)
# # # #                         response = st.write_stream(report_generator(report))
# # # #                         save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, response)
# # # #                         st.session_state.messages.append({"role": "assistant", "content": response})
# # # #                         st.session_state.current_report = response
# # # #                     else:
# # # #                         status.update(label="⚠️ Pipeline Paused", state="error")
# # # #                         st.error("No report was generated. The query might be outside the travel domain.")

# # # #                 except Exception as e:
# # # #                     st.error(f"❌ Error: {e}")
# # # #                     status.update(label="Pipeline Failed", state="error")

# # # #     if "current_report" in st.session_state and st.session_state.current_report:
# # # #         st.markdown("---")
# # # #         st.download_button(
# # # #             label="📥 Download Research",
# # # #             data=st.session_state.current_report,
# # # #             file_name=f"travel_research.txt",
# # # #             mime="text/plain"
# # # #         )

# # # # if __name__ == "__main__":
# # # #     if "logged_in" not in st.session_state:
# # # #         st.session_state.logged_in = False
# # # #     if not st.session_state.logged_in:
# # # #         auth_gate()
# # # #     else:
# # # #         research_interface()
# # # import streamlit as st
# # # import time
# # # import uuid
# # # import asyncio
# # # from main import app as graph_app 
# # # from utils.auth_utils import (
# # #     register_user, 
# # #     authenticate_user, 
# # #     get_user_history, 
# # #     load_past_research,
# # #     save_final_report_to_db
# # # )

# # # # --- PAGE CONFIG ---
# # # st.set_page_config(
# # #     page_title="Deep Travel Research Agent", 
# # #     page_icon="🌀", 
# # #     layout="wide"
# # # )

# # # # Helper for the typewriter effect
# # # def report_generator(text):
# # #     for word in text.split(" "):
# # #         yield word + " "
# # #         time.sleep(0.01)

# # # # --- ASYNC RUNNER FOR LANGGRAPH ---
# # # async def run_research_graph(inputs):
# # #     """Handles async streaming and ensures the FULL accumulated state is captured."""
# # #     final_state = dict(inputs) 
    
# # #     async for chunk in graph_app.astream(inputs, stream_mode="updates"):
# # #         for node_name, output in chunk.items():
# # #             final_state.update(output)
            
# # #             # PROGRESS FEEDBACK
# # #             if node_name == "scoping":
# # #                 if output.get("clarification_needed"):
# # #                     st.toast("🤔 Scoping needs more info...", icon="❓")
# # #                 else:
# # #                     st.info("🔍 **Scoping:** Parameters verified.")
# # #             elif node_name == "research_brief":
# # #                 st.info("📋 **Briefing:** Research tracks created.")
# # #             elif node_name == "deep_research":
# # #                 st.info("🌐 **Deep Research:** Gathering data...")
# # #             elif node_name == "synthesis":
# # #                 st.info("✍️ **Synthesis:** Finalizing report...")

# # #     return final_state

# # # # --- AUTHENTICATION UI ---
# # # def auth_gate():
# # #     st.sidebar.title("🔐 Access Control")
# # #     choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
# # #     if choice == "Sign Up":
# # #         st.title("📝 Create Account")
# # #         new_user = st.text_input("Username")
# # #         new_email = st.text_input("Email")
# # #         new_pass = st.text_input("Password", type="password")
# # #         if st.button("Register"):
# # #             if register_user(new_user, new_email, new_pass):
# # #                 st.success("Registration successful! Please switch to Login.")
# # #             else:
# # #                 st.error("Username or Email already exists.")
# # #     else:
# # #         st.title("🔑 Login")
# # #         user = st.text_input("Username")
# # #         pw = st.text_input("Password", type="password")
# # #         if st.button("Login"):
# # #             uid = authenticate_user(user, pw)
# # #             if uid:
# # #                 st.session_state.logged_in = True
# # #                 st.session_state.user_id = uid
# # #                 st.rerun()
# # #             else:
# # #                 st.error("Invalid credentials.")

# # # # --- RESEARCH INTERFACE ---
# # # def research_interface():
# # #     with st.sidebar:
# # #         st.header(f"👤 User: {st.session_state.user_id}")
# # #         if st.button("Logout"):
# # #             st.session_state.logged_in = False
# # #             st.rerun()
        
# # #         st.markdown("---")
# # #         st.header("📜 Research History")
# # #         history = get_user_history(st.session_state.user_id)
# # #         if history:
# # #             for m_id, query, created_at in history:
# # #                 if st.button(f"📄 {query[:25]}...", key=str(m_id)):
# # #                     report = load_past_research(m_id)
# # #                     st.session_state.messages = [{"role": "assistant", "content": report}]
# # #                     st.session_state.current_report = report
# # #                     st.rerun()

# # #     st.title("🌀 Deep Travel Research Agent")
    
# # #     # 1. ALWAYS render history first
# # #     if "messages" not in st.session_state:
# # #         st.session_state.messages = []

# # #     for message in st.session_state.messages:
# # #         with st.chat_message(message["role"]):
# # #             st.markdown(message["content"])

# # #     # 2. Handle New Input
# # #     if prompt := st.chat_input("Ex: Plan a family trip to Orlando..."):
# # #         current_mission_id = str(uuid.uuid4())
        
# # #         # Immediate UI Update for User Message
# # #         st.session_state.messages.append({"role": "user", "content": prompt})
# # #         with st.chat_message("user"):
# # #             st.markdown(prompt)

# # #         inputs = {
# # #             "user_query": prompt, 
# # #             "user_id": st.session_state.user_id,
# # #             "mission_id": current_mission_id,
# # #             "raw_research_output": []
# # #         }

# # #         # 3. Graph Execution
# # #         with st.chat_message("assistant"):
# # #             final_state = {}
# # #             with st.status("🚀 Processing Research...", expanded=True) as status:
# # #                 try:
# # #                     # Run the graph and capture results
# # #                     final_state = asyncio.run(run_research_graph(inputs))
# # #                     status.update(label="✅ Processing Complete", state="complete", expanded=False)
# # #                 except Exception as e:
# # #                     status.update(label="❌ Pipeline Failed", state="error")
# # #                     st.error(f"Error: {e}")

# # #             # --- CRITICAL: Rendering Logic OUTSIDE of the status block ---
# # #             needs_clarification = final_state.get("clarification_needed", False)
# # #             question = final_state.get("clarification_question")
# # #             report = final_state.get("final_report")

# # #             if needs_clarification and question:
# # #                 st.markdown("### ❓ Information Required")
# # #                 st.warning(question)
# # #                 # Store in session state so it survives the next rerun
# # #                 st.session_state.messages.append({"role": "assistant", "content": f"**Clarification Required:** {question}"})
# # #                 st.rerun() # Force refresh to show the message in the chat history

# # #             elif report:
# # #                 full_response = st.write_stream(report_generator(report))
# # #                 st.session_state.messages.append({"role": "assistant", "content": full_response})
# # #                 st.session_state.current_report = full_response
# # #                 save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, full_response)
# # #                 st.rerun()
# # #             else:
# # #                 st.error("⚠️ No output generated. Check if your Scoping node is returning the correct keys.")
# # #                 # Debugger: See what the graph actually returned
# # #                 with st.expander("Debug: Raw Graph Output"):
# # #                     st.write(final_state)

# # # if __name__ == "__main__":
# # #     if "logged_in" not in st.session_state:
# # #         st.session_state.logged_in = False
# # #     if not st.session_state.logged_in:
# # #         auth_gate()
# # #     else:
# # #         research_interface()
# # import streamlit as st
# # import time
# # import uuid
# # import asyncio
# # from main import app as graph_app 
# # from utils.auth_utils import (
# #     register_user, 
# #     authenticate_user, 
# #     get_user_history, 
# #     load_past_research,
# #     save_final_report_to_db
# # )

# # # --- PAGE CONFIG ---
# # st.set_page_config(
# #     page_title="Deep Travel Research Agent", 
# #     page_icon="🌀", 
# #     layout="wide"
# # )

# # # Helper for the typewriter effect
# # def report_generator(text):
# #     for word in text.split(" "):
# #         yield word + " "
# #         time.sleep(0.01)

# # # --- ASYNC RUNNER FOR LANGGRAPH ---
# # async def run_research_graph(inputs):
# #     """Handles async streaming and ensures the FULL accumulated state is captured."""
# #     # We use mission_id as a thread_id to ensure we can pull state from memory if streaming fails
# #     config = {"configurable": {"thread_id": inputs["mission_id"]}}
# #     final_state = dict(inputs) 
    
# #     async for chunk in graph_app.astream(inputs, config=config, stream_mode="updates"):
# #         for node_name, output in chunk.items():
# #             final_state.update(output)
            
# #             # PROGRESS FEEDBACK
# #             if node_name == "scoping":
# #                 st.info("🔍 **Scoping:** Analyzing parameters...")
# #             elif node_name == "research_brief":
# #                 st.info("📋 **Briefing:** Research tracks created.")
# #             elif node_name == "deep_research":
# #                 st.info("🌐 **Deep Research:** Gathering data...")
# #             elif node_name == "synthesis":
# #                 st.info("✍️ **Synthesis:** Finalizing report...")

# #     # FINAL SAFETY: Pull the absolute final state from the graph's memory (Checkpointer)
# #     # This ensures if 'updates' missed a key, we get it here.
# #     snapshot = await graph_app.aget_state(config)
# #     if snapshot.values:
# #         final_state.update(snapshot.values)

# #     return final_state

# # # --- AUTHENTICATION UI ---
# # def auth_gate():
# #     st.sidebar.title("🔐 Access Control")
# #     choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
# #     if choice == "Sign Up":
# #         st.title("📝 Create Account")
# #         new_user = st.text_input("Username")
# #         new_email = st.text_input("Email")
# #         new_pass = st.text_input("Password", type="password")
# #         if st.button("Register"):
# #             if register_user(new_user, new_email, new_pass):
# #                 st.success("Registration successful! Please switch to Login.")
# #             else:
# #                 st.error("Username or Email already exists.")
# #     else:
# #         st.title("🔑 Login")
# #         user = st.text_input("Username")
# #         pw = st.text_input("Password", type="password")
# #         if st.button("Login"):
# #             uid = authenticate_user(user, pw)
# #             if uid:
# #                 st.session_state.logged_in = True
# #                 st.session_state.user_id = uid
# #                 st.rerun()
# #             else:
# #                 st.error("Invalid credentials.")

# # # --- RESEARCH INTERFACE ---
# # def research_interface():
# #     with st.sidebar:
# #         st.header(f"👤 User: {st.session_state.user_id}")
# #         if st.button("Logout"):
# #             st.session_state.logged_in = False
# #             st.rerun()
        
# #         st.markdown("---")
# #         st.header("📜 Research History")
# #         history = get_user_history(st.session_state.user_id)
# #         if history:
# #             for m_id, query, created_at in history:
# #                 if st.button(f"📄 {query[:25]}...", key=str(m_id)):
# #                     report = load_past_research(m_id)
# #                     st.session_state.messages = [{"role": "assistant", "content": report}]
# #                     st.session_state.current_report = report
# #                     st.rerun()

# #     st.title("🌀 Deep Travel Research Agent")
    
# #     if "messages" not in st.session_state:
# #         st.session_state.messages = []

# #     # Display chat history
# #     for message in st.session_state.messages:
# #         with st.chat_message(message["role"]):
# #             st.markdown(message["content"])

# #     if prompt := st.chat_input("Ex: Plan a family trip to Orlando..."):
# #         current_mission_id = str(uuid.uuid4())
        
# #         st.session_state.messages.append({"role": "user", "content": prompt})
# #         with st.chat_message("user"):
# #             st.markdown(prompt)

# #         inputs = {
# #             "user_query": prompt, 
# #             "user_id": st.session_state.user_id,
# #             "mission_id": current_mission_id,
# #             "raw_research_output": []
# #         }

# #         with st.chat_message("assistant"):
# #             final_state = {}
# #             with st.status("🚀 Processing Research...", expanded=True) as status:
# #                 try:
# #                     final_state = asyncio.run(run_research_graph(inputs))
# #                     status.update(label="✅ Processing Complete", state="complete", expanded=False)
# #                 except Exception as e:
# #                     status.update(label="❌ Pipeline Failed", state="error")
# #                     st.error(f"Error: {e}")

# #             # --- RENDERING LOGIC ---
# #             # Extract keys
# #             needs_clarification = final_state.get("clarification_needed", False)
# #             # Logic fallback: if graph signaled 'clarification_needed' via next_node
# #             if final_state.get("next_node") == "clarification_needed":
# #                 needs_clarification = True
                
# #             question = final_state.get("clarification_question")
# #             report = final_state.get("final_report")

# #             if needs_clarification and question:
# #                 st.markdown("### ❓ Information Required")
# #                 st.warning(question)
# #                 st.session_state.messages.append({"role": "assistant", "content": f"**Clarification Required:** {question}"})
            
# #             elif report and len(report) > 10:
# #                 full_response = st.write_stream(report_generator(report))
# #                 st.session_state.messages.append({"role": "assistant", "content": full_response})
# #                 st.session_state.current_report = full_response
# #                 save_final_report_to_db(st.session_state.user_id, current_mission_id, prompt, full_response)
            
# #             else:
# #                 st.error("⚠️ No output generated.")
# #                 with st.expander("Debug: Raw Graph State"):
# #                     st.json(final_state)

# #     # DOWNLOAD SECTION
# #     if "current_report" in st.session_state and st.session_state.current_report:
# #         st.markdown("---")
# #         st.download_button(
# #             label="📥 Download Research",
# #             data=st.session_state.current_report,
# #             file_name=f"travel_research.txt",
# #             mime="text/plain"
# #         )

# # if __name__ == "__main__":
# #     if "logged_in" not in st.session_state:
# #         st.session_state.logged_in = False
# #     if not st.session_state.logged_in:
# #         auth_gate()
# #     else:
# #         research_interface()
# import streamlit as st
# import time
# import uuid
# import asyncio
# from main import app as graph_app 
# from utils.auth_utils import (
#     register_user, 
#     authenticate_user, 
#     get_user_history, 
#     load_past_research,
#     save_final_report_to_db
# )

# # --- PAGE CONFIG ---
# st.set_page_config(
#     page_title="Deep Travel Research Agent", 
#     page_icon="🌀", 
#     layout="wide"
# )

# # Helper for the typewriter effect
# def report_generator(text):
#     for word in text.split(" "):
#         yield word + " "
#         time.sleep(0.01)

# # --- ASYNC RUNNER FOR LANGGRAPH ---
# async def run_research_graph(inputs, thread_id):
#     """Handles async streaming with a persistent thread_id for memory."""
#     # This config is what allows the agent to "remember" previous questions
#     config = {"configurable": {"thread_id": thread_id}}
#     final_state = dict(inputs) 
    
#     async for chunk in graph_app.astream(inputs, config=config, stream_mode="updates"):
#         for node_name, output in chunk.items():
#             final_state.update(output)
            
#             # PROGRESS FEEDBACK
#             if node_name == "scoping":
#                 st.info("🔍 **Scoping:** Analyzing parameters...")
#             elif node_name == "deep_research":
#                 st.info("🌐 **Deep Research:** Gathering data...")
#             elif node_name == "synthesis":
#                 st.info("✍️ **Synthesis:** Finalizing report...")

#     # Pull the absolute final state from the checkpointer memory
#     snapshot = await graph_app.aget_state(config)
#     if snapshot.values:
#         final_state.update(snapshot.values)

#     return final_state

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
#     # Initialize Mission ID and Messages
#     if "current_mission_id" not in st.session_state:
#         st.session_state.current_mission_id = str(uuid.uuid4())
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     with st.sidebar:
#         st.header(f"👤 User: {st.session_state.user_id}")
        
#         # Reset Button for new research
#         if st.button("➕ New Research Mission", use_container_width=True):
#             st.session_state.current_mission_id = str(uuid.uuid4())
#             st.session_state.messages = []
#             st.session_state.current_report = None
#             st.rerun()

#         if st.button("Logout"):
#             st.session_state.logged_in = False
#             st.rerun()
        
#         st.markdown("---")
#         st.header("📜 Research History")
#         history = get_user_history(st.session_state.user_id)
#         if history:
#             for m_id, query, created_at in history:
#                 if st.button(f"📄 {query[:25]}...", key=str(m_id)):
#                     report = load_past_research(m_id)
#                     st.session_state.messages = [{"role": "assistant", "content": report}]
#                     st.session_state.current_report = report
#                     st.session_state.current_mission_id = str(m_id)
#                     st.rerun()

#     st.title("🌀 Deep Travel Research Agent")
    
#     # Display chat history
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     # Chat Input
#     if prompt := st.chat_input("Ask a question or provide clarification..."):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         inputs = {
#             "user_query": prompt, 
#             "user_id": st.session_state.user_id,
#             "mission_id": st.session_state.current_mission_id,
#             "raw_research_output": []
#         }

#         with st.chat_message("assistant"):
#             final_state = {}
#             with st.status("🚀 Thinking...", expanded=True) as status:
#                 try:
#                     # Run the graph using the persistent mission_id
#                     final_state = asyncio.run(run_research_graph(inputs, st.session_state.current_mission_id))
#                     status.update(label="✅ Analysis Complete", state="complete", expanded=False)
#                 except Exception as e:
#                     status.update(label="❌ Pipeline Failed", state="error")
#                     st.error(f"Error: {e}")

#             # --- RENDERING LOGIC ---
#             needs_clarification = final_state.get("clarification_needed", False)
#             # Fallback for routing logic
#             if final_state.get("next_node") == "clarification_needed":
#                 needs_clarification = True
                
#             question = final_state.get("clarification_question")
#             report = final_state.get("final_report")

#             if needs_clarification and question:
#                 st.markdown("### ❓ Information Required")
#                 st.warning(question)
#                 st.session_state.messages.append({"role": "assistant", "content": f"**Clarification Required:** {question}"})
            
#             elif report and len(report) > 10:
#                 full_response = st.write_stream(report_generator(report))
#                 st.session_state.messages.append({"role": "assistant", "content": full_response})
#                 st.session_state.current_report = full_response
#                 save_final_report_to_db(st.session_state.user_id, st.session_state.current_mission_id, prompt, full_response)
            
#             else:
#                 st.error("⚠️ No output generated.")
#                 with st.expander("Debug: Raw Graph State"):
#                     st.json(final_state)

#     # DOWNLOAD SECTION
#     if "current_report" in st.session_state and st.session_state.current_report:
#         st.markdown("---")
#         st.download_button(
#             label="📥 Download Research Report",
#             data=st.session_state.current_report,
#             file_name=f"travel_research_{st.session_state.current_mission_id}.txt",
#             mime="text/plain"
#         )

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

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Deep Travel Research Agent", 
    page_icon="🌀", 
    layout="wide"
)

# Helper for the typewriter animation effect
def report_generator(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)

# --- 2. ASYNC BRIDGE (Streamlit to LangGraph) ---
async def run_research_graph(inputs, thread_id):
    """
    Connects to the Graph. Uses thread_id to ensure memory persistence 
    so clarifications are remembered.
    """
    config = {"configurable": {"thread_id": thread_id}}
    final_state = dict(inputs) 
    
    # Stream the updates so we can show progress in the UI
    async for chunk in graph_app.astream(inputs, config=config, stream_mode="updates"):
        for node_name, output in chunk.items():
            final_state.update(output)
            
            # Live progress feedback via Streamlit Toasts
            if node_name == "scoping":
                st.toast("🔍 Scoping your travel request...", icon="🕵️")
            elif node_name == "deep_research":
                st.toast("🌐 Searching the web for real-time data...", icon="🔎")
            elif node_name == "synthesis":
                st.toast("✍️ Drafting your custom itinerary...", icon="📝")

    # Final Check: Pull the latest state from the Checkpointer memory
    snapshot = await graph_app.aget_state(config)
    if snapshot.values:
        final_state.update(snapshot.values)

    return final_state

# --- 3. AUTHENTICATION GATE ---
def auth_gate():
    st.sidebar.title("🔐 Access Control")
    choice = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    
    if choice == "Sign Up":
        st.title("📝 Create Account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("Registration successful! Please login.")
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

# --- 4. RESEARCH INTERFACE (The Controller) ---
def research_interface():
    # Persistent Session State Initialization
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_mission_id" not in st.session_state:
        st.session_state.current_mission_id = str(uuid.uuid4())
    if "current_report" not in st.session_state:
        st.session_state.current_report = None

    # --- SIDEBAR: Profile & History ---
    with st.sidebar:
        st.header(f"👤 User: {st.session_state.user_id}")
        
        # Start a fresh topic
        if st.button("➕ New Research Mission", use_container_width=True):
            st.session_state.current_mission_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.current_report = None
            st.rerun()

        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        st.markdown("---")
        st.subheader("📜 Recent Research")
        history = get_user_history(st.session_state.user_id)
        if history:
            for m_id, query, _ in history:
                if st.button(f"📄 {query[:25]}...", key=str(m_id)):
                    report = load_past_research(m_id)
                    st.session_state.messages = [{"role": "assistant", "content": report}]
                    st.session_state.current_report = report
                    st.session_state.current_mission_id = str(m_id)
                    st.rerun()

    # --- MAIN CHAT AREA ---
    st.title("🌀 Deep Travel Research Agent")
    st.caption(f"Mission ID: `{st.session_state.current_mission_id}`")

    # Render Historical Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle New User Input
    if prompt := st.chat_input("Where should we research next?"):
        # 1. Add user message to UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Prepare Graph Input
        inputs = {
            "user_query": prompt, 
            "user_id": st.session_state.user_id,
            "mission_id": st.session_state.current_mission_id
        }

        # 3. Execute Graph and Handle Output
        with st.chat_message("assistant"):
            with st.status("🚀 Processing Research Pipeline...", expanded=True) as status:
                try:
                    final_state = asyncio.run(
                        run_research_graph(inputs, st.session_state.current_mission_id)
                    )
                    status.update(label="✅ Analysis Complete", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="❌ Pipeline Failed", state="error")
                    st.error(f"Error: {e}")
                    final_state = {}

            # --- Logic: Determine next UI step ---
            needs_clarify = final_state.get("clarification_needed", False)
            question = final_state.get("clarification_question")
            report = final_state.get("final_report")

            if needs_clarify and question:
                st.markdown("### ❓ Information Required")
                st.warning(question)
                st.session_state.messages.append({"role": "assistant", "content": f"**Question:** {question}"})
            
            elif report:
                # Typewriter streaming effect
                full_response = st.write_stream(report_generator(report))
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.current_report = full_response
                # Save to DB
                save_final_report_to_db(st.session_state.user_id, st.session_state.current_mission_id, prompt, full_response)
            
            else:
                st.error("⚠️ The agent completed its run but no output was found.")
                with st.expander("Debug Details"):
                    st.json(final_state)

    # --- DOWNLOAD SECTION ---
    if st.session_state.current_report:
        st.markdown("---")
        st.download_button(
            label="📥 Download Research as Text",
            data=st.session_state.current_report,
            file_name=f"research_report_{st.session_state.current_mission_id}.txt",
            mime="text/plain"
        )

# --- 5. EXECUTION ENTRY POINT ---
if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        auth_gate()
    else:
        research_interface()