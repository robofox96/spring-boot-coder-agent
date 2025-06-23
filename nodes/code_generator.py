from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

import json
from states.states import CodeState

SYSTEM_PROMPT = """
You are a Java software engineer given a task to add or update the existing Java code base.
Your job is to:
1. Understand the code change requirement given by the orchestrator.
2. Understand the existing code base and verify the changes that need to be done. Give more importance to the existing code base and try to reuse it as much as possible.
3. Make the necessary code changes to the code base. Utilize the existing code base as much as possible.
4. Verify if all the dependencies required for the code changes are present in the pom.xml file. If not, add the necessary dependencies to the pom.xml file.
5. Verify the necessary import statements are present in the code files. If not, add the necessary import statements.
6. Finally once the code changes are done, respond with the code changes summary.

You have access to tools that can read files, create or update files, and show the project structure. Use these tools to understand the existing code base and make the necessary code changes.
In case any of these tools return a False or return an Error message, you should assume that the tool failed to perform the operation and you should not proceed with the code changes.

Adhere to the best practices and coding standards while making the code changes.
"""

NEXT_STEP_PROMPT = """
Given the below requirement by the orchestrator for a Java project, make the code changes or carry out the actions as described in the requirement:
${requirement}
"""

from tools.file_tools import *

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([read_file, create_or_update_file, show_project_structure])

# Define a lang graph node that generates code based on the requirement
def generate_code(state: CodeState):
    print("In generate_code node")
    """
    Generate code based on the requirement provided in the state.
    The state should contain the 'requirement' key with the requirement text.
    """
    curr_step = state["current_implementation_step"]
    coding_state_info = state["coding_impl"][curr_step]
    step_info = state["coding_plan"]["steps"][coding_state_info["coding_step"]-1]
    if coding_state_info["coding_started"] is False:
        state["messages"].append(HumanMessage(content=SYSTEM_PROMPT))
        state["messages"].append(HumanMessage(content=NEXT_STEP_PROMPT.replace("${requirement}", dict_to_string(step_info))))
        coding_state_info["coding_started"] = True

    # Here you would implement the logic to generate code based on the requirement.
    state["messages"].append(llm_with_tools.invoke(state["messages"]))
    coding_state_info["coding_done"] = True
    state["coding_impl"][curr_step] = coding_state_info
    # state["messages"].extend(coding_state_info["messages"])
    return state


def dict_to_string(obj):
    return json.dumps(obj, indent=2, sort_keys=True)

# print(
#     generate_code(
# {'coding_plan': {'steps': [{'step': 1, 'description': 'Update pom.xml'}]}, 'impl_started': True, 'impl_done': False, 'coding_impl': {1: {'coding_started': False, 'messages': [], 'coding_step': 1, 'overall_requirement': 'Implement a new feature.', 'coding_done': False}}, 'feature_requirement': 'Implement a new feature.', 'current_implementation_step': 1, 'messages': [], 'planning_started': False}
#     )
# )