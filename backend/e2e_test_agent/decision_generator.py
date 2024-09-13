import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from playwright.async_api import Page
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_core.messages import AIMessage

from e2e_test_agent.states import AgentState
from e2e_test_agent import all_actions
from utils.config import config

rules = [f"{key}: {all_actions[key].__doc__}" for key in all_actions.keys()]

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
embeddings = OpenAIEmbeddings(
    api_key=config.openai_api_key, model="text-embedding-3-small"
)


class ActionData(BaseModel):
    url: Optional[str] = Field(None, title="Url to be navigated")
    selector: Optional[str] = Field(
        None, title="CSS selector of element which action applied for"
    )
    text: Optional[str] = Field(None, title="Text to be typed")
    file_path: Optional[str] = Field(None, title="File path to be added")


class Command(BaseModel):
    action: str = Field(
        ...,
        title="Action to be performed",
        description=f"Valid options are: {', '.join(all_actions.keys())}, END",
    )
    data: ActionData = Field(
        default_factory=dict,
        title="Action data",
        description=(
            "A dictionary containing various data required to perform the action. "
            "This dictionary should include additional values based on the action type: "
            f"{', '.join(rules)}"
        ),
    )
    description: str = Field(
        ...,
        title="Command description",
        description="A brief description of the action to be performed.",
    )


fast_llm = ChatOpenAI(api_key=config.openai_api_key, model="gpt-3.5-turbo")
long_context_llm = ChatOpenAI(api_key=config.openai_api_key, model="gpt-4o")


find_possible_dom_details_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Base on below requirement, provide possible doms and details which action to be applied",
        ),
        ("user", "Requirement: {requirement}"),
        MessagesPlaceholder(variable_name="messages", optional=True),
    ]
)
find_possible_dom_details = find_possible_dom_details_prompt | fast_llm


async def index_page(page: Page):
    page_content = await page.content()
    split_docs = splitter.create_documents([page_content])
    try:
        vectorstore = await SKLearnVectorStore.afrom_documents(
            split_docs,
            embedding=embeddings,
        )
        retriever = vectorstore.as_retriever()
        return retriever
    except Exception as e:
        print(e)
        return None


async def retrieve(state: AgentState):
    page = state["page"]
    retriever = await index_page(page)
    coros = (index_page(page), find_possible_dom_details.ainvoke(state))
    results = await asyncio.gather(*coros)
    retriever = results[0]
    possible_dom_details: str = results[1].content
    try:
        docs = await retriever.ainvoke(possible_dom_details)
        formatted = "\n".join([f"<Part/>\n{doc.page_content}\n</Part>" for doc in docs])
        return {"docs": formatted, **state}
    except Exception as e:
        print(e)

    return {"docs": "", **state}


command_gen_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Analyze the provided page parts and determine the appropriate action to meet the user's requirement and based on what we have done so far. Populate the 'data' field with the necessary information as a dictionary. If all actions are completed or a step fails, respond with 'END' for the action. Ensure the 'data' field contains any additional information needed to perform the action.
            """,
        ),
        ("user", "Requirement: {requirement}\nPage Parts: {docs}"),
        MessagesPlaceholder(variable_name="messages", optional=True),
    ]
)
command_generator = (
    retrieve | command_gen_prompt | long_context_llm.with_structured_output(Command)
)


async def decision_generator(state: AgentState):
    try:
        command: Command = await command_generator.ainvoke(state)
        ai_message = AIMessage(content=command.description)
        return {
            **state,
            "action": command.action,
            "data": command.data,
            "messages": [ai_message],
        }
    except Exception as e:
        print(e)
        return {**state, "action": "END"}
