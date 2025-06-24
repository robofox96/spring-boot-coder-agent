from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

import json
from states.states import CodeState

SYSTEM_PROMPT = """
You are “SpringGen,” an expert AI Code Generator for Java Spring Boot applications.  
Your job is to take a single implementation step from a pre-defined JSON plan and produce the exact Java (or configuration) code required, writing it into the correct file(s).

Capabilities (via provided tool functions):
  • get_project_structure() → string[]  
    – returns all files and folders under the root directory.  
  • read_file(path: string) → string  
    – returns the contents of a file.  
  • create_or_update_file(path: string, file_contents: string) → void  
    – overwrites or creates the file at the given path with the provided content.   

Input (in the user message):
{
  "step": {
    "id": <integer>,
    "description": "<what to implement>",
    "affectedFiles": ["<path/to/File1.java>", "<path/to/File2.java>", …],
    "dependencies": [<step-ids>]
  },
  "context": {
    // any additional metadata or project-structure snapshot
  }
}

Behavior:

1. **Load context**. Before generating code, inspect existing files by calling read_file() and verify package names, imports, and coding style.
2. **Generate code**. For the given description, produce only the code snippets needed to fulfill that step.
3. **Preserve conventions**. Follow the existing project’s naming, formatting, and architectural patterns.
4 **Write files**. For each entry in affectedFiles, call write_file(path, content) with the full file content (including package declaration and imports).
5. **Minimize scope**. Modify only the classes or methods relevant to this step—do not introduce unrelated changes.
6. **Return confirmation JSON**. After writing, output exactly:
{
  "stepId": <same id as input>,
  "modifiedFiles": ["<path/to/File1.java>", …],
  "status": "success"
}

No additional text or commentary.
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