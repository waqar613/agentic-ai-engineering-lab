import streamlit as st
from crewai import Agent, Task, Crew, LLM

# Page Configuration & Styling
st.set_page_config(
    page_title="AI Code Studio",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS for Modern UI
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Title & Sidebar Header
st.title("⚡ Modern AI Coding Dashboard")
st.caption("Powered by Local Ollama & CrewAI")

# Sidebar Status & Info
with st.sidebar:
    st.header("⚙️ Agent Settings")
    st.success("🟢 Local LLM Connected")
    st.info("Model: `qwen2.5-coder:7b`")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize LLM & Agent
@st.cache_resource
def get_agent():
    local_llm = LLM(
        model="ollama/qwen2.5-coder:7b",
        base_url="http://localhost:11434"
    )
    return Agent(
        role="Senior Python Developer",
        goal="Write clean, production-ready, and efficient Python code with helpful comments.",
        backstory="You are an expert software developer who writes complete, runnable code.",
        verbose=True,
        allow_delegation=False,
        llm=local_llm
    )

coder_agent = get_agent()

# Chat History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Box
if user_prompt := st.chat_input("Apna coding task ya instruction yahan likhein..."):
    # 1. User message chat mein add aur display karein
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Agent Response Generate Karein
    with st.chat_message("assistant"):
        with st.spinner("⚡ Agent code generate kar raha hai..."):
            try:
                coding_task = Task(
                    description=user_prompt,
                    expected_output="A clean, functional, complete Python script with proper comments.",
                    agent=coder_agent
                )
                crew = Crew(
                    agents=[coder_agent],
                    tasks=[coding_task],
                    verbose=True
                )
                result = crew.kickoff()
                response_text = str(result)
                
                # Assistant message display aur session mein save karein
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"Error: {e}")