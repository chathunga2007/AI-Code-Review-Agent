import os
from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv

# .env file eken API key eka load karagannawa
load_dotenv()

# Gemini aluth model name eka (gemini-2.5-flash) use karannawa
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

# 1. Code Reviewer Agent
code_reviewer = Agent(
    role="Senior Software Code Reviewer",
    goal="Analyze the provided source code for bugs, logic errors, and security vulnerabilities.",
    backstory=(
        "You are an expert software architect with 10+ years of experience."
        " You carefully inspect code to ensure high quality and clean architecture."
    ),
    verbose=True,
    llm=gemini_llm,
)

# 2. Technical Writer Agent
tech_writer = Agent(
    role="Technical Documentation Writer",
    goal="Create clear, professional README documentation and code explanation reports based on the review.",
    backstory=(
        "You are a skilled technical writer who turns complex code reviews"
        " into easy-to-understand Markdown documentation."
    ),
    verbose=True,
    llm=gemini_llm,
)

# Review task eka define krnw
review_task = Task(
    description=(
        "Read the code in the sample.py file, analyze its logic, find any"
        " potential issues or improvements."
    ),
    expected_output="A detailed bulleted list of code bugs, issues, and suggested improvements.",
    agent=code_reviewer,
)

# Documentation task eka define krnw
documentation_task = Task(
    description=(
        "Take the review output and generate a professional Markdown report"
        " explaining what the code does and how to improve it."
    ),
    expected_output="A clean Markdown format report with code breakdown and recommendations.",
    agent=tech_writer,
)

# Crew eka set karala tasks run krnw
code_review_crew = Crew(
    agents=[code_reviewer, tech_writer],
    tasks=[review_task, documentation_task],
    process=Process.sequential,
    verbose=True,
)

print("## AI Agent is analyzing your code with Gemini 2.5 Flash... ##")
result = code_review_crew.kickoff()

print("\n\n########################")
print("## FINAL AGENT REPORT ##")
print("########################\n")
print(result)