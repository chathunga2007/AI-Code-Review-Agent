import os
from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv
import streamlit as st

# .env file eken keys load karagannawa
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="AI Code Review & Documentation Agent",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AI Code Review & Documentation Agent")
st.write(
    "Upload your source code file or paste code directly, select your"
    " language, and let our AI Architecture Crew analyze it!"
)

# Initialize session state for history if not exists
if "history" not in st.session_state:
  st.session_state.history = []

# Sidebar for options
st.sidebar.header("⚙️ Configuration")
language = st.sidebar.selectbox(
    "Select Programming Language",
    ["Java", "Python", "JavaScript", "TypeScript", "HTML/CSS", "C++", "Other"],
)

input_method = st.radio(
    "Choose input method:", ["Paste Code Text", "Upload Code File"]
)

user_code = ""

if input_method == "Upload Code File":
  uploaded_file = st.file_uploader(
      "Upload your code file",
      type=["py", "java", "js", "ts", "html", "css", "cpp", "txt"],
  )
  if uploaded_file is not None:
    user_code = uploaded_file.read().decode("utf-8")
    st.code(user_code, language=language.lower())
else:
  user_code = st.text_area(
      "Paste your source code here:",
      height=220,
      placeholder="Paste your source code here...",
  )

# Sidebar History Section
st.sidebar.header("📜 Review History")
selected_history_report = None
if st.session_state.history:
  for i, past_review in enumerate(st.session_state.history):
    if st.sidebar.button(
        f"Review {i+1} ({past_review['lang']})", key=f"hist_{i}"
    ):
      selected_history_report = past_review
else:
  st.sidebar.write("No previous reviews yet.")

# Sidebar Footer / Copyright Section Added Here!
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='text-align: center; color: #a0a0a0; font-size: 12px;'>Developed"
    " with ❤️ by <b>Chathunga Bimsara</b><br>© 2026 All Rights Reserved</p>",
    unsafe_allow_html=True,
)

if st.button("🚀 Run AI Review & Generate Docs"):
  if not user_code.strip():
    st.warning("Please provide some source code first!")
  else:
    with st.spinner("AI Agents are analyzing your code architecture..."):

      # Setup Gemini LLM
      api_key = os.getenv("GEMINI_API_KEY")
      if not api_key:
        st.error("GEMINI_API_KEY not found in .env file!")
      else:
        gemini_llm = LLM(
            model="gemini/gemini-2.5-flash", api_key=api_key, temperature=0.2
        )

        # 1. Define Agents
        code_reviewer = Agent(
            role="Senior Software Code Reviewer",
            goal=(
                f"Analyze the provided {language} source code for bugs, logic"
                " errors, and security vulnerabilities."
            ),
            backstory=(
                "You are an expert software architect with 10+ years of"
                " experience ensuring high quality and clean architecture."
            ),
            verbose=False,
            llm=gemini_llm,
        )

        tech_writer = Agent(
            role="Technical Documentation Writer",
            goal=(
                "Create clear, professional README documentation and code"
                " explanation reports based on the review."
            ),
            backstory=(
                "You are a skilled technical writer who turns complex code"
                " reviews into easy-to-understand Markdown documentation."
            ),
            verbose=False,
            llm=gemini_llm,
        )

        # 2. Define Tasks
        review_task = Task(
            description=(
                f"Read and analyze the following {language} source code"
                f" carefully. Find any bugs, logic errors, architectural issues,"
                f" or improvements:\n\n{user_code}"
            ),
            expected_output=(
                "A detailed bulleted list of code bugs, issues, and suggested"
                " improvements."
            ),
            agent=code_reviewer,
        )

        documentation_task = Task(
            description=(
                "Take the review output and generate a professional Markdown"
                " report explaining what the code does, breaking down its"
                " components, and providing recommendations."
            ),
            expected_output=(
                "A clean Markdown format report with code breakdown and"
                " recommendations."
            ),
            agent=tech_writer,
        )

        # 3. Create Crew and Kickoff
        code_review_crew = Crew(
            agents=[code_reviewer, tech_writer],
            tasks=[review_task, documentation_task],
            process=Process.sequential,
            verbose=False,
        )

        result = code_review_crew.kickoff()
        report_text = str(result)

        # Save to history session state
        st.session_state.history.append({"lang": language, "report": report_text})

        # Display Result in Streamlit UI
        st.success("Analysis Complete!")
        st.markdown("### 📄 Final Agent Report")
        st.markdown(report_text)

        # Download Button for Report
        st.download_button(
            label="📥 Download Markdown Report",
            data=report_text,
            file_name="Code_Review_Report.md",
            mime="text/markdown",
        )

# If user clicked a history item from sidebar, show it
if selected_history_report:
  st.markdown(f"### 📄 Past Report ({selected_history_report['lang']})")
  st.markdown(selected_history_report["report"])