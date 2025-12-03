from src.model.prompt import prompt, prompt_1, prompt_2
from langchain_google_genai import ChatGoogleGenerativeAI
from src.setup import GOOGLE_API_KEY
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import AgentState
from langchain_core.messages import AIMessage
from langchain.tools import tool, ToolRuntime
from langgraph.prebuilt.tool_node import tools_condition, ToolNode
from src.db import connection
import json


class State(AgentState):
    client_id: str
    name: str
    email: str


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    disable_streaming=False,
)

chain = prompt | llm

tables_description = """
Database schema:

Table Product:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- price: NUMERIC NOT NULL
- stock: INT NOT NULL

Table Customer:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- email: TEXT NOT NULL

Table Orders:
- id: SERIAL PRIMARY KEY
- customer_id: INT NOT NULL REFERENCES Customer(id)
- order_date: TIMESTAMP NOT NULL DEFAULT NOW()

Table OrderItem:
- id: SERIAL PRIMARY KEY
- order_id: INT NOT NULL REFERENCES Orders(id)
- product_id: INT NOT NULL REFERENCES Product(id)
- quantity: INT NOT NULL


"""


tables_description_detailed = """
Database schema with example data (1 row per table):

Table Product:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- price: NUMERIC NOT NULL
- stock: INT NOT NULL
Example row:
1, 'Laptop', 1200, 10

Table Customer:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- email: TEXT NOT NULL
Example row:
1, 'Alice', 'alice@example.com'

Table Orders:
- id: SERIAL PRIMARY KEY
- customer_id: INT NOT NULL REFERENCES Customer(id)
- order_date: TIMESTAMP NOT NULL DEFAULT NOW()
Example row:
1, 1, '2025-11-20'

Table OrderItem:
- id: SERIAL PRIMARY KEY
- order_id: INT NOT NULL REFERENCES Orders(id)
- product_id: INT NOT NULL REFERENCES Product(id)
- quantity: INT NOT NULL
Example row:
1, 1, 1, 1  -- Alice bought 1 Laptop
"""


@tool
async def get_data_db(table: str, column: str) -> str:
    """Dùng để lấy tên tất cả sản phẩm"""

    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT name FROM product")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def process(state: State) -> State:
    response = await chain.ainvoke(
        {
            "tables_description": tables_description_detailed,
            "messages": state.get("messages"),
            "name": state.get("name"),
            "email": state.get("email"),
        }
    )
    state.update(messages=[AIMessage(content=response.content)])
    return state


tools = ToolNode([get_data_db])
graph = StateGraph(State)
graph.add_node("process", process)
graph.add_node("tools", tools)
graph.set_entry_point("process")
graph.add_conditional_edges(
    "process", tools_condition, {"tools": "tools", "__end__": "__end__"}
)
graph.add_edge("tools", "process")
graph = graph.compile(checkpointer=MemorySaver())
