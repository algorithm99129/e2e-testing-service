from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage

from e2e_test_agent.actions import BaseAction
from e2e_test_agent.states import AgentState


class ClickElement(BaseAction):
    """
    Click element action is used to click any element of the page. You must provide CSS selector of element which to be clicked.
    """

    action_type = "click_element"

    async def run(self, state: AgentState) -> Optional[Dict[str, Any]]:
        page = state["page"]
        selector = state["data"].selector

        if selector is None:
            raise Exception("Can't find selector")

        try:
            await page.click(selector)
            ai_message = AIMessage(content=f"Clicked {selector} element successfully")
            return {"messages": [ai_message]}
        except Exception as e:
            error_message = AIMessage(
                content=f"Failed to click {selector} element: {str(e)}"
            )
            return {"messages": [error_message]}
