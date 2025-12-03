from fastapi import Query


from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import os
from src.model.chain import chain, graph
from src.db import connection
import json
import re
from langchain_core.messages import HumanMessage, AIMessageChunk
from fastapi import HTTPException
import asyncio


class SQLRequest(BaseModel):
    sql: str


clients = {}

router = APIRouter()

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static"))


@router.get("/", response_class=HTMLResponse)
async def get_chat_page():
    html_path = os.path.join(STATIC_DIR, "query.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h3>Chat page not found.</h3>", status_code=404)
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@router.get("/handshake")
async def handshake(
    full_name: str,
    email: str,
    client_id: str,
):

    if not full_name.strip() or not email.strip() or not client_id.strip():
        raise HTTPException(status_code=400, detail="Thiếu thông tin bắt buộc.")

    clients[client_id] = {"full_name": full_name.strip(), "email": email.strip()}

    try:
        cursor = connection.cursor()

        check_sql = "SELECT id FROM Customer WHERE email = %s"
        cursor.execute(check_sql, (email.strip(),))
        exists = cursor.fetchone()

        if not exists:
            insert_sql = "INSERT INTO Customer (name, email) VALUES (%s, %s)"
            cursor.execute(insert_sql, (full_name.strip(), email.strip()))
            connection.commit()

        cursor.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi DB: {str(e)}")

    return {"success": True, "client_id": client_id}


@router.get("/query")
async def query(message: str, client_id: str):
    async def generate():
        full_response = ""
        name = clients[client_id].get("full_name")
        email = clients[client_id].get("email")
        input_state = {
            "client_id": client_id,
            "name": name,
            "email": email,
            "messages": HumanMessage(content=message),
        }

        config = {
            "configurable": {
                "thread_id": client_id,
            }
        }
        async for chunk in graph.astream(input_state, config, stream_mode="messages"):
            response, meta = chunk
            if isinstance(response, AIMessageChunk):
                full_response += response.content
                for c in response.content:
                    await asyncio.sleep(0.01)
                    yield f"data: {json.dumps({'type': 'chunk', 'response': c}, ensure_ascii=False)}\n\n"

        match = re.search(
            r"---SQL START---(.*?)---SQL END---", full_response, re.DOTALL
        )
        sql = match.group(1).strip() if match else ""

        yield f"data: {json.dumps({'type': 'sql', 'response': sql}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/get_data")
async def get_data(request: SQLRequest):
    sql = request.sql
    try:
        cursor = connection.cursor()
        cursor.execute(sql)

        sql_type = sql.strip().split()[0].upper()
        if sql_type == "SELECT":
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
        else:
            connection.commit()
            data = [{"successfully": cursor.rowcount}]

        cursor.close()
        return data

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
