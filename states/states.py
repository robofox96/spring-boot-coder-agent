from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class IndCodingState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    overall_requirement: str
    code_changes_description: str
    coding_done: bool
    coding_step: int
    coding_started: bool

class CodeState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    overall_messages: list[BaseMessage]
    planning_started: bool
    coding_plan: dict
    feature_requirement: str
    impl_started: bool
    impl_done: bool
    coding_impl: dict[int, IndCodingState]
    current_implementation_step: int
