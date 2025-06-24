import re

from langchain_openai import ChatOpenAI

from states.states import CodeState
from tools.file_tools import build_project

# llm = ChatOpenAI(model="gpt-4o")

SUMMARY_PROMPT = """
You are a Java software engineer responsible for analyzing the build logs and summarizing the build process.
Your job is to:
1. Review the build logs provided in the state.
2. Identify any errors or warnings that occurred during the build process.
3. Provide a clear and concise summary of the build process errors. This will be used to generate a plan for fixing the errors.

You have access to the build logs in the state. Use these logs to analyze the build process and summarize it.
Here is the build log:
${build_log}
"""

def builder_node(state: CodeState):
    """
    This node is responsible for building the project and preparing the code for execution.
    It tries to build the project and returns whether the build was successful or not.
    If the build fails, it returns the relevant error messages from the build process.
    """
    print("In builder node")
    try:
        # Attempt to build the project
        build_project()
        state["build_success"] = True
    except Exception as e:
        # If the build fails, capture the error and set the state accordingly
        state["build_success"] = False
        # build_summary = llm.invoke(
        #     SUMMARY_PROMPT.replace("${build_log}", str(e))
        # )
        state["build_summary"] = str(extract_failures_and_warnings(str(e)))
    return state

def decide_next_step_after_build(state: CodeState) -> str:
    """
    This node decides the next step after the build process.
    If the build was successful, it returns '__end__' to indicate completion.
    If the build failed, it returns 'code_generator_node' to retry code generation.
    """
    if state["build_success"]:
        return "__end__"
    state["messages"] = []
    return "error_handler_node"


def extract_failures_and_warnings(log_str):
    """
    Parses the given Maven log string. If a "BUILD FAILURE" is detected,
    returns a formatted string of all lines starting with [ERROR] or [WARNING].
    Otherwise, returns an empty string.
    """
    error_re   = re.compile(r'^\[ERROR\]')
    warning_re = re.compile(r'^\[WARNING\]')

    lines = log_str.splitlines()
    build_failed = any("BUILD FAILURE" in line for line in lines)

    if not build_failed:
        return ""

    # Collect errors and warnings
    errors = [line.strip() for line in lines if error_re.match(line)]
    warnings = [line.strip() for line in lines if warning_re.match(line)]

    formatted = []

    if errors:
        formatted.append("=== ERRORS ===")
        formatted.extend(errors)

    if warnings:
        formatted.append("\n=== WARNINGS ===")
        formatted.extend(warnings)

    return "\n".join(formatted)

# print(builder_node(
#     {
#         "messages": [],
#         "build_success": False,
#         "build_summary": "",
#         "impl_started": False,
#         "impl_done": False,
#         "coding_plan": {},
#         "coding_impl": {},
#         "current_implementation_step": 0,
#         "planning_started": False,
#         "feature_requirement": "Look at each file and fix the dependencies required in the overall project. Make sure to update the pom.xml file with the necessary dependencies.",
#         "overall_messages": []
#     }
# ))