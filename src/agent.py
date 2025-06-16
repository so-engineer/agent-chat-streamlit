import io
import uuid
from typing import Annotated, Any

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt
from PIL import Image
from typing_extensions import TypedDict

from src.setup import setup_config, setup_logger

# Setup
logger = setup_logger()
model, api_key, tavily_api_key, search_web_mode = setup_config()


# Tools
try:
    search_web = TavilySearch(max_results=2, tavily_api_key=tavily_api_key)
except Exception as e:
    logger.debug(f"Web search failed: {e}")
    raise


@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human.

    This tool implements LangGraph's Human-in-the-Loop functionality.
    It is used when the AI:
    - needs help making critical decisions
    - is uncertain about the best course of action
    - requires human judgment on complex matters

    The conversation flow is interrupted to delegate the decision-making
    to the user, ensuring better accuracy and reliability.
    """
    logger.debug(f"human_assistance/start: {query}")
    human_response = interrupt({"query": query})
    logger.debug(f"human_assistance/end: {human_response}")
    return human_response["data"]


class State(TypedDict):
    messages: Annotated[list, add_messages]


class Agent:
    def __init__(self):
        if search_web_mode:
            self.tools = [search_web, human_assistance]
        else:
            self.tools = [human_assistance]
        self.llm_with_tools = ChatOpenAI(model=model, api_key=api_key).bind_tools(
            self.tools
        )
        self.config = {
            "configurable": {"thread_id": uuid.uuid4()},
            "recursion_limit": 10,
        }
        self.graph = self.build_graph()
        self.graph_image = self.display_graph()

    # Graph
    def build_graph(self) -> Any:
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        graph_builder.add_edge("tools", "chatbot")
        checkpointer = MemorySaver()
        return graph_builder.compile(checkpointer=checkpointer)

    # Utility
    def display_graph(self) -> Image.Image:
        png_data = self.graph.get_graph().draw_mermaid_png()
        return Image.open(io.BytesIO(png_data))

    # Nodes
    def chatbot(self, state: State) -> dict[str, list]:
        # Add system message if not present at the beginning
        if not any(isinstance(message, SystemMessage) for message in state["messages"]):
            system_prompt = SystemMessage(
                content=(
                    "You are a helpful assistant. "
                    "IMPORTANT: Do not hesitate to use the human_assistance tool "
                    "whenever you are uncertain or need more details. It is better "
                    "to ask for clarification than to make assumptions. "
                    "Use only one tool per turn, with a single call per tool."
                )
            )
            state["messages"].insert(0, system_prompt)
        logger.debug(f"state['messages']: {state['messages']}")
        message = self.llm_with_tools.invoke(state["messages"])
        logger.debug(f"tool_calls/len: {len(message.tool_calls)}")
        logger.debug(f"tool_calls: {message.tool_calls}")
        # When multiple tool calls are detected, use only the first one
        # to prevent parallel tool execution and ensure sequential processing
        if len(message.tool_calls) > 1:
            message.tool_calls = [message.tool_calls[0]]
        # assert len(message.tool_calls) <= 1
        return {"messages": [message]}
