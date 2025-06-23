import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

import tools.file_tools
from states.states import CodeState

SYSTEM_PROMPT = """
You are a Spring Boot Java Backend Developer given a task to add or update the existing Spring Boot Backend Application code base. You are responsible for planning the code changes based on the requirements provided by the orchestrator.
Make sure to follow the best practices and utilize the existing code base as much as possible.
Your job is to:
1. Understand the requirement given by the orchestrator.
2. Collect all the necessary information about the existing code base that is needed to implement the feature. Use the tools provided for this purpose.
3. Make a detailed step by step plan for the necessary code changes to the code base.
4. Review the plan to verify if it is satisfying the requirements.
5. If review highlights needs for change, make the changes to the plan otherwise proceed with the plan.
6. Repeat steps 2-5 until the plan is satisfactory.
7. Finally respond wih the detailed plan of code changes that need to be implemented in a JSON format. Refer the OUTPUT_EXAMPLE to understand the format. 

You have access to tools that can read current existing files and show the overall project structure. 

OUTPUT_EXAMPLE:
{
    "overview": "This plan outlines the steps to implement a new feature in the Java project.",
    "steps": [
        {
            "step": 1,
            "description": "Update `pom.xml`",
            "file": "pom.xml",
            "action": "update",
            "changes": "Detailed description of any changes needed in the pom.xml file ... "
        },
        {
            "step": 2,
            "description": "Create the User Entity class",
            "file": "src/main/java/org/example/testproject/model/User.java",
            "action": "create",
            "changes": "Detailed description of the User class implementation, including fields, methods, annotations, etc."
        }
    ]
}

Respond with only the JSON formatted plan and nothing else. This Json should be directly parsable. Do not include any additional text or explanations.
"""

NEXT_STEP_PROMPT = """
Given the below requirement by the orchestrator for a Java project, create a detailed plan for the code changes that will be needed to implement the feature.:
${requirement}

Make sure to respond with only the JSON formatted plan and nothing else. Refer the OUTPUT EXAMPLE in the SYSTEM_PROMPT for the expected format.
"""

from tools.file_tools import *

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([read_file, show_project_structure])

# Define a lang graph node that generates code based on the requirement
def generate_plan_node(state: CodeState):
    print("In planner node")
    """
    Generate plan based on the requirement provided in the state.
    The state should contain the 'requirement' key with the requirement text.
    """
    if state["planning_started"] is False:
        state["messages"].append(HumanMessage(content=SYSTEM_PROMPT))
        state["messages"].append(HumanMessage(content=NEXT_STEP_PROMPT.replace("${requirement}", state["feature_requirement"])))
        state["planning_started"] = True
    else:
        state["messages"].append(HumanMessage(content="Continuing with the planning..."))

    # Here you would implement the logic to generate code based on the requirement.
    state["messages"].append(llm_with_tools.invoke(state["messages"]))
    return state