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

#Build the graph
builder = StateGraph(CodeState)

def tool_node_decider(state: CodeState) -> str:
    """
    This node decides whether to call a tool or not based on the LLM response.
    If the response contains a tool call, it returns the 'tools' node.
    Otherwise, it returns the 'implementer_node'.
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "implementer_node"

def tool_node_decider_v2(state: CodeState) -> str:
    """
    This node decides whether to call a tool or not based on the LLM response.
    If the response contains a tool call, it returns the 'tools' node.
    Otherwise, it returns the 'implementer_node'.
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "code_tools"
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
builder.add_node("implementer_node", implement_coding_plan_node)

# Define the edges
builder.add_edge(START, "code_planner_node")
builder.add_conditional_edges("code_planner_node", tool_node_decider) #tools_condition is an inbuilt function that checks if the LLM response contains a tool call or not
# builder.add_conditional_edges("tools", decide_post_tool_node)
builder.add_edge("tools", "code_planner_node")
builder.add_edge("code_tools", "code_generator_node")
# builder.add_edge("code_planner_node", "implementer_node")
builder.add_conditional_edges("code_generator_node", tool_node_decider_v2) #tools_condition is an inbuilt function that checks if the LLM response contains a tool call or not
builder.add_conditional_edges("implementer_node", decide_next_step_node)

# Define memory for the graph
memory = MemorySaver()

# Add memory to the graph and compile
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "thread_1"}, "recursion_limit": 100}
code_state = {
    "feature_requirement": "Create a backend application for Movie Ticket Booking. Use internal H2 database for storage.",
    "planning_started": False,
    "impl_started": False,
    "impl_done": False,
    "coding_plan": {},
    "coding_impl": {},
    "current_implementation_step": 0,
    "messages": [],
    "overall_messages": []
}

# Run the graph
result = graph.invoke(code_state, config=config)

# result = implement_coding_plan_node(result)

for m in result['overall_messages']:
    m.pretty_print()