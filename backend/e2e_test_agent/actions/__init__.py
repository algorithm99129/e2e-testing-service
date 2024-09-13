from abc import ABC, abstractmethod
import importlib
import logging
import pathlib
from typing import Any, Dict, Optional, Union

from e2e_test_agent.states import AgentState


class BaseAction(ABC):
    """
    Abstract base class for actions

    Any action within the actions folder that implements this BaseAction class
    will automatically get registered in the action_dispatcher upon initialization.
    This registration enables the action_dispatcher to delegate actions to the appropriate
    action based on the action type. This mechanism ensures a modular and scalable approach
    to handling different types of actions within this project.
    """

    @property
    @abstractmethod
    def action_type(self) -> str:
        """
        Define the type of action.
        """
        pass

    @abstractmethod
    async def run(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """
        Execute the action with the given arguments.

        The returned action is what will be updated agent state.
        """
        pass


class ActionDispatcher:
    def __init__(self):
        self.actions: Dict[str, BaseAction] = {}

    def register_action(self, action_type: str, action: BaseAction):
        """
        Register an action to the dispatcher.

        :param action_type: The type of action.
        :param action: The action instance.
        """
        self.actions[action_type] = action

    def load_actions(
        self, directory: Union[str, pathlib.Path] = pathlib.Path(__file__).parent
    ):
        for path in pathlib.Path(directory).rglob("*.py"):
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, BaseAction)
                    and obj != BaseAction
                ):
                    self.register_action(obj.action_type, obj())

    @classmethod
    def get_dispatcher_with_loaded_actions(cls, directory: str = None):
        """
        Create a ActionDispatcher instance and automatically load actions from the specified directory.
        If no directory is provided, it defaults to the directory of this file. Additionally, logs which actions were loaded.

        :param directory: The directory from which to load actions. Defaults to the directory of this file.
        :return: An instance of ActionDispatcher with actions loaded.
        """
        if directory is None:
            directory = pathlib.Path(__file__).parent
        dispatcher = cls()
        dispatcher.load_actions(directory)
        for action_type in dispatcher.actions.keys():
            logging.info(f"Loaded action for type: {action_type}")
        return dispatcher
