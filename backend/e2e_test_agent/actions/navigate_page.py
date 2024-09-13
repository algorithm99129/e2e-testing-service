from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage

from e2e_test_agent.actions import BaseAction
from e2e_test_agent.states import AgentState


class NavigatePage(BaseAction):
    """
    Navigate page to specific URL. You must provide 'url' to be navigated to the data field.
    """

    action_type = "navigate_page"

    async def run(self, state: AgentState) -> Optional[Dict[str, Any]]:
        page = state["page"]
        url = state["data"].url

        if url is None:
            raise Exception("Can't find url")

        try:
            await page.goto(url)
        except Exception as e:
            error_message = AIMessage(content=f"Failed to navigate to {url}: {str(e)}")
            return {"messages": [error_message]}

        ai_message = AIMessage(content=f"Navigated to {url} successfully.")
        return {"messages": [ai_message]}
