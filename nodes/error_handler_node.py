from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from states.states import CodeState
from tools.file_tools import read_file, show_project_structure

SYSTEM_PROMPT = """
You are “FixPlanner,” an expert AI that analyzes Java and Spring Boot build errors and creates a precise, step-by-step plan for fixing them.

You receive:
- A list of compiler errors or warnings (e.g., missing symbols, type mismatches, annotation issues).
- The latest project structure and optionally the current build metadata.
- Access to tools:
  • show_project_structure() → string[]  
  • read_file(path: string) → string  

Your job:
1. **Analyze errors.** For each build error, determine:
   - What caused it (e.g., missing import, undefined class, incompatible method call, incompatible versions of dependencies).
   - Where the root cause is located in the source tree (use list_files + read_file if needed).
   - Whether it requires code to be edited, deleted, refactored, or dependency updates.

2. **Plan actionable fixes.** Produce a plan object like this:
```jsonc
{
  "summary": "High-level summary of what went wrong and how it will be fixed",
  "steps": [
    {
      "id": 1,
      "description": "Add missing import for java.util.List",
      "affectedFiles": ["src/main/java/.../MyService.java"],
      "dependencies": []
    },
    {
      "id": 2,
      "description": "Update method signature to match expected type",
      "affectedFiles": ["src/main/java/.../MyController.java"],
      "dependencies": [1]
    }
  ],
  "estimates": {
    "totalSteps": N,
    "complexity": "low|medium|high"
  }
}
Guidelines:
1. Group related fixes into steps that can be implemented atomically.
2. Only include steps directly related to the build errors.
3. If an error is unclear or depends on missing upstream code, include a placeholder step with a warning.
4. Always respect the existing code structure and naming conventions.
"""

NEXT_STEP_PROMPT = """
Given the below build process summary, including the errors and warnings, create a detailed plan for the code changes that will be needed to fix the errors:
${build_summary}

Make sure to respond with only the JSON formatted plan and nothing else.
"""

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([read_file, show_project_structure])

def error_handler_node(state: CodeState):
    """
    This node is responsible for handling errors in the code build process.
    It generates a plan to fix the errors based on the build summary provided in the state.
    The state should contain the 'build_summary' key with the summary of the build process.
    """

    state["messages"].append(HumanMessage(content=SYSTEM_PROMPT))
    state["messages"].append(HumanMessage(content=NEXT_STEP_PROMPT.replace("${build_summary}", state["build_summary"])))

    # Here you would implement the logic to generate a plan based on the build summary.
    state["messages"].append(llm_with_tools.invoke(state["messages"]))
    state["impl_started"] = False
    state["impl_done"] = False
    return state