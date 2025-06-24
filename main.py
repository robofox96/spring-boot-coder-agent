from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import add_messages, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import AIMessage, HumanMessage, AnyMessage

from dotenv import load_dotenv

from states.states import CodeState, IndCodingState

load_dotenv()

from tools.file_tools import *
from nodes.code_generator import generate_code
from nodes.code_planner import generate_plan_node
from nodes.orchestrator import implement_coding_plan_node, decide_next_step_node
from nodes.error_handler_node import error_handler_node
from nodes.builder_node import builder_node, decide_next_step_after_build

#Build the graph
builder = StateGraph(CodeState)

def plan_tool_node_decider(state: CodeState) -> str:
    """
    This node decides whether to call a tool or not based on the LLM response.
    If the response contains a tool call, it returns the 'tools' node.
    Otherwise, it returns the 'implementer_node'.
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "implementer_node"

def code_tool_node_decider(state: CodeState) -> str:
    """
    This node decides whether to call a tool or not based on the LLM response.
    If the response contains a tool call, it returns the 'tools' node.
    Otherwise, it returns the 'implementer_node'.
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "code_tools"
    return "implementer_node"

def error_handler_tool_node_decider(state: CodeState) -> str:
    """
    This node decides whether to call a tool or not based on the LLM response.
    If the response contains a tool call, it returns the 'tools' node.
    Otherwise, it returns the 'implementer_node'.
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "error_handler_tools"
    return "implementer_node"

def decide_post_tool_node(state: CodeState) -> str:
    """
    This node decides the next step based on the current state after a tool call.
    It checks if coding is done and returns the appropriate message.
    """
    if state["impl_started"] is False:
        return "code_planner_node"
    return "code_generator_node"

# Define the nodes
builder.add_node("code_planner_node", generate_plan_node)
builder.add_node("code_generator_node", generate_code)
builder.add_node("tools", ToolNode([read_file, show_project_structure])) # ToolNode is a prebuilt node that handles tool calls
builder.add_node("code_tools", ToolNode([read_file, show_project_structure, create_or_update_file])) # ToolNode for file creation or update
builder.add_node("error_handler_tools", ToolNode([read_file, show_project_structure]))
builder.add_node("implementer_node", implement_coding_plan_node)
builder.add_node("error_handler_node", error_handler_node)
builder.add_node("builder_node", builder_node)

# Define the edges
builder.add_edge(START, "code_planner_node")
builder.add_conditional_edges("code_planner_node", plan_tool_node_decider)

builder.add_edge("tools", "code_planner_node")
builder.add_edge("code_tools", "code_generator_node")
builder.add_edge("error_handler_tools", "error_handler_node")

builder.add_conditional_edges("code_generator_node", code_tool_node_decider)
builder.add_conditional_edges("implementer_node", decide_next_step_node)

builder.add_conditional_edges("builder_node", decide_next_step_after_build)
builder.add_conditional_edges("error_handler_node", error_handler_tool_node_decider)

# Define memory for the graph
memory = MemorySaver()

# Add memory to the graph and compile
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "thread_1"}, "recursion_limit": 100}
code_state = {
    "feature_requirement": "The build process of the project is failing due to context load issues in Test files. Fix the context load issues in the Test files.",
    "planning_started": False,
    "impl_started": False,
    "impl_done": False,
    "coding_plan": {},
    "coding_impl": {},
    "build_success": False,
    "build_summary": "",
    "current_implementation_step": 0,
    "messages": [],
    "overall_messages": [],
    "cycles": 3
}

# Run the graph
result = graph.invoke(code_state, config=config)

for m in result['overall_messages']:
    m.pretty_print()