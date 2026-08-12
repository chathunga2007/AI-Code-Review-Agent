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

# Sidebar for options
st.sidebar.header("⚙️ Configuration")
language = st.sidebar.selectbox(
    "Select Programming Language",
    ["Python", "Java", "JavaScript", "TypeScript", "HTML/CSS", "C++", "Other"],
)

input_method = st.radio(
    "Choose input method:", ["Upload Code File", "Paste Code Text"]
)

user_code = ""

if input_method == "Upload Code File":
  uploaded_file = st.file_uploader(
      "Upload your code file", type=["py", "java", "js", "ts", "html", "css", "cpp"]
  )
  if uploaded_file is not None:
    user_code = uploaded_file.read().decode("utf-8")
    st.code(user_code, language=language.lower())
else:
  user_code = st.text_area(
      "Paste your source code here:",
      height=200,
      placeholder="def add(a, b):\n    return a + b",
  )

if st.button("🚀 Run AI Review & Generate Docs"):
  if not user_code.strip():
    st.warning("Please provide some source code first!")
  else:
    with st.spinner("AI Agents are analyzing your code architecture..."):

      # 1. Temporarily save code into sample file
      with open("sample.py", "w", encoding="utf-8") as f:
        f.write(user_code)

      # 2. Setup Gemini LLM
      api_key = os.getenv("GEMINI_API_KEY")
      if not api_key:
        st.error("GEMINI_API_KEY not found in .env file!")
      else:
        gemini_llm = LLM(
            model="gemini/gemini-2.5-flash", api_key=api_key, temperature=0.2
        )

        # 3. Define Agents
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

        # 4. Define Tasks
        review_task = Task(
            description=(
                "Read the code in the sample.py file, analyze its logic, and"
                " find any potential issues or improvements."
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
                " report explaining what the code does and how to improve it."
            ),
            expected_output=(
                "A clean Markdown format report with code breakdown and"
                " recommendations."
            ),
            agent=tech_writer,
        )

        # 5. Create Crew and Kickoff
        code_review_crew = Crew(
            agents=[code_reviewer, tech_writer],
            tasks=[review_task, documentation_task],
            process=Process.sequential,
            verbose=False,
        )

        result = code_review_crew.kickoff()
        report_text = str(result)

        # 6. Display Result in Streamlit UI
        st.success("Analysis Complete!")
        st.markdown("### 📄 Final Agent Report")
        st.markdown(report_text)

        # 7. Download Button for Report
        st.download_button(
            label="📥 Download Markdown Report",
            data=report_text,
            file_name="Code_Review_Report.md",
            mime="text/markdown",
        )