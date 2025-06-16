import streamlit as st
from langchain_core.messages import AIMessage
from langgraph.types import Command

from src.agent import Agent
from src.setup import setup_logger

# Setup
logger = setup_logger()


def process_stream(user_input: dict[str, list[dict[str, str]]] | Command) -> None:
    # Get events generator from graph.stream
    # events is a generator that yields each event in the conversation flow
    events = st.session_state["graph"].stream(
        user_input,
        config=st.session_state["config"],
        stream_mode="values",
    )

    # Convert generator to list to process the last event
    list_events = list(events)
    last_event = list_events[-1]

    # DEBUG
    # st.write("list_events: ", list_events)
    # st.write("last_event: ", last_event)
    # st.write("state", st.session_state["graph"].get_state(st.session_state["config"]))

    if "__interrupt__" in last_event:
        st.session_state["interrupted"] = True
        st.session_state["interrupt_value"] = last_event["__interrupt__"][0].value[
            "query"
        ]
        # If necessary, add a custom message
        content = (
            f"{st.session_state['interrupt_value']}\n\n"
            "⚠️ **回答するための情報が不足しています。確認してください。**"
        )
        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": content,
            }
        )
        with st.chat_message("assistant"):
            st.markdown(content)
    elif "messages" in last_event:
        st.session_state["interrupted"] = False
        st.session_state["interrupt_value"] = None

        for message in last_event["messages"]:
            if isinstance(message, AIMessage) and message.content:
                ai_message = str(message.content)
        st.session_state["messages"].append(
            {"role": "assistant", "content": ai_message}
        )
        with st.chat_message("assistant"):
            st.markdown(ai_message)
    else:
        logger.debug(f"Unexpected event type received: {last_event}")
        raise


def main() -> None:
    st.set_page_config(page_title="Agent Chat", page_icon="🤖")
    st.title("Agent Chat 🤖")

    if "agent" not in st.session_state:
        st.session_state["agent"] = Agent()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "graph" not in st.session_state:
        st.session_state["graph"] = st.session_state["agent"].graph
        st.session_state["graph_image"] = st.session_state["agent"].graph_image
        st.session_state["config"] = st.session_state["agent"].config
        st.session_state["interrupted"] = False
        st.session_state["interrupt_value"] = None

    # display graph
    if "graph_image" in st.session_state:
        content = (
            "こんにちは。何かお手伝いできることはありますか？\n\n"
            "回答するための情報が不足している場合はユーザーに尋ねます。\n\n"
        )
        with st.chat_message("assistant"):
            st.markdown(content)
            st.image(st.session_state["graph_image"], width=300)

    # display chat history messages
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Type a message...")

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            user_input: dict[str, list[dict[str, str]]] | Command
            if not st.session_state["interrupted"]:
                user_input = {"messages": [{"role": "user", "content": prompt}]}
                process_stream(user_input)
            else:
                # If interrupted, prompt input from the user
                user_input = Command(resume={"data": prompt})
                process_stream(user_input)
        except Exception as e:
            logger.debug(f"Failed to process_stream: {e}")
            st.write("タスクの実行に失敗しました。確認してください。")


if __name__ == "__main__":
    main()
