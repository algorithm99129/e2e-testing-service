from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage

from e2e_test_agent.actions import BaseAction
from e2e_test_agent.states import AgentState


class InputFile(BaseAction):
    """
    Input file action is used to select file for input[type=file] element of the page. You must provide CSS 'selector' of element which to be clicked and 'file_path' to be selected.
    """

    action_type = "input_file"

    async def run(self, state: AgentState) -> Optional[Dict[str, Any]]:
        page = state["page"]
        selector = state["data"].selector
        file_path = state["data"].file_path

        if selector is None or file_path is None:
            raise Exception("Can't find selector and file_path")

        try:
            await page.set_input_files(selector, file_path)
            ai_message = AIMessage(
                content=f"Selected {file_path} successfully to {selector} element"
            )
            return {"messages": [ai_message]}
        except Exception as e:
            error_message = AIMessage(
                content=f"Failed to select {file_path} to {selector} element: {str(e)}"
            )
            return {"messages": [error_message]}
