import streamlit as st
from crewai import Agent, Task, Crew, LLM
from gtts import gTTS
import os

# Page Config
st.set_page_config(
    page_title="AI Code Studio Pro",
    page_icon="⚡",
    layout="wide"
)

# Custom Professional Styling with Dark Theme Chat Input Border Fix
st.markdown("""
    <style>
    /* Permanent Dark Theme Base */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Hide Streamlit Top Header Toolbar */
    header[data-testid="stHeader"] {
        visibility: hidden;
        display: none;
    }

    /* Professional Dark Theme Chat Input Container & Border */
    [data-testid="stChatInput"] {
        background-color: #161b22 !important;
        border: 1.5px solid #30363d !important;
        border-radius: 12px !important;
    }

    .stChatInput textarea {
        color: #ffffff !important;
        background-color: transparent !important;
        font-weight: 500 !important;
    }

    [data-testid="stChatMessageContent"] {
        color: #ffffff !important;
    }

    .stSpinner > div {
        color: #ffeb3b !important;
        font-weight: bold !important;
    }

    pre {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
    }

    /* Visible File Uploader Styling */
    [data-testid="stFileUploader"] {
        background-color: #161b22 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #30363d !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: #21262d !important;
        border: 2px dashed #484f58 !important;
    }
    [data-testid="stFileUploader"] section span, 
    [data-testid="stFileUploader"] section div, 
    [data-testid="stFileUploader"] section small {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ AI Code Studio Pro")
st.caption("Professional Full-Stack Code Auditor, File Fixer & Interactive Assistant")

# Sidebar
with st.sidebar:
    st.header("⚙️ Agent Settings")
    st.success("🟢 Ollama Connected")
    st.info("Model: `qwen2.5-coder:7b`")
    
    if "uploaded_file_name" in st.session_state:
        st.markdown("---")
        st.markdown(f"📄 **Active File:** `{st.session_state.uploaded_file_name}`")
        if st.button("❌ Remove File", use_container_width=True):
            del st.session_state["uploaded_file_content"]
            del st.session_state["uploaded_file_name"]
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        if "uploaded_file_content" in st.session_state:
            del st.session_state["uploaded_file_content"]
        if "uploaded_file_name" in st.session_state:
            del st.session_state["uploaded_file_name"]
        if os.path.exists("response.mp3"):
            os.remove("response.mp3")
        st.rerun()

# LLM & Agent Setup
@st.cache_resource
def get_agent():
    local_llm = LLM(
        model="ollama/qwen2.5-coder:7b",
        base_url="http://localhost:11434"
    )
    return Agent(
        role="Senior Full Stack Code Auditor & Engineer",
        goal="Analyze code, detect bugs, optimize performance, write comprehensive comments, and generate clean runnable code.",
        backstory="You are a world-class software engineer expert in static code analysis, debugging, and code refactoring.",
        verbose=True,
        allow_delegation=False,
        llm=local_llm
    )

coder_agent = get_agent()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "download_data" in message:
            st.download_button(
                label=f"📥 Download Fixed {message['file_name']}",
                data=message["download_data"],
                file_name=message["file_name"],
                mime="text/plain",
                key=message.get("btn_key", "download_btn")
            )

# --- VISIBLE PROFESSIONAL FILE UPLOADER PANEL ---
st.markdown("---")
st.markdown("### 📎 Attach Code File (.py, .js, .html, .css, .json, .txt)")
uploaded_file = st.file_uploader(
    "Apni file yahan upload karein:", 
    type=["py", "js", "html", "css", "json", "txt"],
    label_visibility="collapsed"
)

selected_quick_task = None

if uploaded_file:
    st.session_state.uploaded_file_content = uploaded_file.getvalue().decode("utf-8")
    st.session_state.uploaded_file_name = uploaded_file.name
    st.success(f"📎 File Attached Successfully: {uploaded_file.name}")

# Auto-Task Action Buttons if File Attached
if "uploaded_file_name" in st.session_state:
    st.markdown(f"#### 🛠️ Quick Tasks for `{st.session_state.uploaded_file_name}`:")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("🔍 Find Errors & Fix", use_container_width=True):
            selected_quick_task = "Is file ke saare errors find karein, explain karein aur complete fixed code provide karein."
    with q2:
        if st.button("🚀 Optimize Code", use_container_width=True):
            selected_quick_task = "Is file ke code ko optimize aur fast banayein, sath hi updated code dein."
    with q3:
        if st.button("📝 Add Comments", use_container_width=True):
            selected_quick_task = "Is file ke har function par clear comments add karein."
    with q4:
        if st.button("🧹 Clean & Format", use_container_width=True):
            selected_quick_task = "Is file ke code ko clean aur proper formatting ke sath rewrite karein."

# Bottom Chat Input
user_prompt = st.chat_input("Yahan apni instruction type karein...")

final_execution_prompt = None
if selected_quick_task:
    final_execution_prompt = selected_quick_task
elif user_prompt:
    final_execution_prompt = user_prompt

# Execution Logic
if final_execution_prompt:
    task_description = final_execution_prompt
    if "uploaded_file_content" in st.session_state:
        task_description = (
            f"User Instruction: {final_execution_prompt}\n\n"
            f"--- UPLOADED FILE ({st.session_state.uploaded_file_name}) CONTENT ---\n"
            f"{st.session_state.uploaded_file_content}\n"
            f"----------------------------------------\n"
            f"If user requested fixing or modifying code, provide the full updated file code inside a single markdown code block (```)."
        )

    st.session_state.messages.append({"role": "user", "content": final_execution_prompt})
    with st.chat_message("user"):
        st.markdown(final_execution_prompt)

    with st.chat_message("assistant"):
        with st.spinner("⚡ Agent code analyze kar raha hai..."):
            try:
                coding_task = Task(
                    description=task_description,
                    expected_output="Detailed review and complete runnable updated code in markdown codeblock if requested.",
                    agent=coder_agent
                )
                crew = Crew(
                    agents=[coder_agent],
                    tasks=[coding_task],
                    verbose=True
                )
                result = crew.kickoff()
                response_text = str(result)
                
                st.markdown(response_text)
                
                tts = gTTS(text="Task complete ho gaya hai.", lang='en')
                audio_path = "response.mp3"
                tts.save(audio_path)
                st.audio(audio_path, format="audio/mp3", autoplay=False)
                
                msg_data = {"role": "assistant", "content": response_text}
                
                if "uploaded_file_name" in st.session_state:
                    fixed_content = response_text
                    if "```" in response_text:
                        parts = response_text.split("```")
                        if len(parts) >= 3:
                            fixed_content = parts[1].split("\n", 1)[-1]
                    
                    download_filename = f"fixed_{st.session_state.uploaded_file_name}"
                    btn_unique_key = f"dl_btn_{len(st.session_state.messages)}"
                    st.download_button(
                        label=f"📥 Download Updated File ({download_filename})",
                        data=fixed_content,
                        file_name=download_filename,
                        mime="text/plain",
                        key=btn_unique_key
                    )
                    msg_data["download_data"] = fixed_content
                    msg_data["file_name"] = download_filename
                    msg_data["btn_key"] = btn_unique_key

                st.session_state.messages.append(msg_data)
                
            except Exception as e:
                st.error(f"Error: {e}")