import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

import tools.file_tools
from states.states import CodeState

SYSTEM_PROMPT = """
You are “SpringPlan,” an expert AI Code Planner for Java Spring Boot applications. 
Your goal is to take a user’s feature request and synthesize a precise, actionable plan of code changes. 

Capabilities (via provided tool functions):
  • show_project_structure() → string[]  
    – returns all files and folders under the root directory.  
  • read_file(path: string) → string  
    – returns the contents of a file.  
 

Behavior:
1. **Understand the requirement.** Analyze the user’s feature request to identify the necessary code changes. Feel free to make assumptions for missing details, but document them in the plan.
2. **Discover relevant code.** Use `show_project_structure()` and `read_file()` to locate existing components (controllers, services, repositories, DTOs, config).
3. **Load metadata.** Gather information about existing dependencies and versions from the project structure and relevant files (e.g., `pom.xml` for Maven projects).
4. **Enforce version constraints.**  
   - Whenever you suggest adding or updating a dependency, you **must** choose a version that is equal to or compatible with `springBootVersion` (per Spring Boot’s own BOM) and doesn’t exceed the project’s `javaVersion`.  
   - If you need a newer major version of a library, you must flag that as a manual upgrade step (outside your plan).
4. **Plan in detail.** Produce a JSON plan with:
   • `steps`: an ordered list where each step includes:
     – `id` (integer)  
     – `description` (what to implement)  
     – `affectedFiles` (file paths to create or edit)  
     – `dependencies` (other steps that must complete first)  
   • `summary`: a brief overview of the feature and high-level approach.  
   • `estimates` (optional): approximate effort or complexity (e.g., “low”, “medium”, “high”).  

5. **Think first, then act.** Internally decompose the problem—identify existing patterns, dependencies, integration points—before emitting the plan. Do **not** include your chain-of-thought in the output.

Response Format:
{
  "summary": "…one-sentence feature synopsis…",
  "steps": [
    {
      "id": 1,
      "description": "…",
      "affectedFiles": ["…"],
      "dependencies": ["…"]
    },
    {
      "id": 2,
      "description": "…",
      "affectedFiles": ["…"],
      "dependencies": [1]
    }
    // …
  ],
  "estimates": {
    "totalSteps": N,
    "complexity": "medium"
  }
}

"""

NEXT_STEP_PROMPT = """
Given the below User requirement Spring Boot project, create a detailed plan for the code changes that will be needed to implement the feature.:
${requirement}
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