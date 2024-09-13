import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from io import BytesIO

from playwright.async_api import async_playwright
from langgraph.graph import END, StateGraph

from e2e_test_agent.decision_generator import decision_generator
from e2e_test_agent.states import AgentState
from e2e_test_agent import all_actions


def visualize_graph(graph):
    image_bytes = graph.get_graph().draw_png()
    image_stream = BytesIO(image_bytes)
    img = mpimg.imread(image_stream, format="png")

    plt.imshow(img)
    plt.axis("off")
    plt.show()


class E2eTestingAgent:
    def __init__(self) -> None:
        self.e2e_test_graph = None

    async def ainvoke(self, topic: str, show_graph: bool = False):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=None)
            page = await browser.new_page()

            if browser is None or page is None:
                raise Exception(
                    "Failed to create browser and new page using playwright"
                )

            initial_state = {"requirement": topic, "page": page}

            e2e_test_graph = await self._build()

            if show_graph:
                visualize_graph(e2e_test_graph)

            final_step = None
            async for step in e2e_test_graph.astream(initial_state):
                name = next(iter(step))
                print(name)
                print("-- ", str(step[name]["messages"]))
                if END in step:
                    final_step = step
                    break

            if not final_step:
                final_step = step

            await browser.close()

    async def _build(self):
        builder = StateGraph(AgentState)

        decision_generator_key = "decision_generator"
        builder.add_node(decision_generator_key, decision_generator)
        for key in all_actions.keys():
            builder.add_node(key, all_actions[key].run)
            builder.add_edge(key, decision_generator_key)

        def route_actions(state: AgentState):
            action = state["action"]
            if action == "END":
                return END
            return action

        builder.add_conditional_edges(decision_generator_key, route_actions)
        builder.set_entry_point(decision_generator_key)

        return builder.compile().with_config(run_name="E2E Testing")
