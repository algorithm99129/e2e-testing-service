from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage

from e2e_test_agent.actions import BaseAction
from e2e_test_agent.states import AgentState


class TypeText(BaseAction):
    """
    Type text to input or textarea element. You must provide CSS 'selector' of element which to be clicked and 'text' to be typed.
    """

    action_type = "type_text"

    async def run(self, state: AgentState) -> Optional[Dict[str, Any]]:
        page = state["page"]
        selector = state["data"].selector
        text = state["data"].text

        if selector is None or text is None:
            raise Exception("Can't find selector and text")

        try:
            await page.fill(selector, text)
            ai_message = AIMessage(content=f"Typed {text} to {selector} element")
            return {"messages": [ai_message]}
        except Exception as e:
            error_message = AIMessage(
                content=f"Failed to type {text} to {selector} element: {str(e)}"
            )
            return {"messages": [error_message]}
