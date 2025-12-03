from src.model.prompt import prompt_sales_order, prompt_sql
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

chain = prompt_sales_order | llm

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
- product_id: INT NOT NULL REFERENCES Product(id)
- quantity: INT NOT NULL
"""


tables_description_detailed = """
Database schema with example data and purpose of each table:

Table Product:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- price: NUMERIC NOT NULL
- stock: INT NOT NULL
Purpose: Lưu thông tin sản phẩm mà cửa hàng bán, bao gồm tên, giá và số lượng tồn kho.
Example row:
1, 'Laptop', 1200, 10

Table Customer:
- id: SERIAL PRIMARY KEY
- name: TEXT NOT NULL
- email: TEXT NOT NULL
Purpose: Lưu thông tin khách hàng, bao gồm tên và email để phục vụ quản lý đơn hàng và liên hệ.
Example row:
1, 'Alice', 'alice@example.com'

Table Orders:
- id: SERIAL PRIMARY KEY
- customer_id: INT NOT NULL REFERENCES Customer(id)
- product_id: INT NOT NULL REFERENCES Product(id)
- quantity: INT NOT NULL
Purpose: Lưu các đơn hàng mà khách hàng đã đặt, mỗi đơn hàng liên kết với một khách hàng và một sản phẩm cụ thể, kèm số lượng.
Example row:
1, 1, 2, 1  -- Alice đặt 1 Mouse
"""


@tool
async def get_data_db() -> str:
    """Dùng để lấy tên chính xác của tất cả sản trong database dựa theo tên người dùng nói."""
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
