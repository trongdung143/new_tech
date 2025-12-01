from src.model.prompt import prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from src.setup import GOOGLE_API_KEY
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import AgentState
from langchain_core.messages import AIMessage


class State(AgentState):
    client_id: str


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    disable_streaming=False,
)

chain = prompt | llm


async def process(state: State) -> State:
    response = await chain.ainvoke({"messages": state.get("messages")})
    state.update(messages=[AIMessage(content=response.content)])
    return state


graph = StateGraph(State)
graph.add_node("process", process)
graph.set_entry_point("process")

graph = graph.compile(checkpointer=MemorySaver())
