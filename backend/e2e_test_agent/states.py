from typing import Annotated, Any, Dict, List, TypedDict

from langchain_core.messages import BaseMessage
from playwright.async_api import Page


def add_messages(left, right):
    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]
    return left + right


class AgentState(TypedDict):
    page: Page
    action: str
    data: Dict[str, Any]
    requirement: str
    messages: Annotated[List[BaseMessage], add_messages]
