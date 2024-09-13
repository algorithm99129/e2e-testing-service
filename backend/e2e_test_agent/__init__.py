from e2e_test_agent.actions import ActionDispatcher

action_dispatcher = ActionDispatcher.get_dispatcher_with_loaded_actions()
all_actions = action_dispatcher.actions
