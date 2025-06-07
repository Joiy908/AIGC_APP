import mimetypes
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from examples.custom_llm import CozeLLM
from examples.custom_reactagent import (
    StopSignal,
    StreamEvent,
    ToolCallResultMessage,
)
from examples.custom_workflow import (
    ReActAgent,
    api_tool,
    datetime_tool,
    docs_tool,
    # llm,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 处理windows 下返回 js MIME type 为 text/plain
    mimetypes.init()
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')
    mimetypes.add_type('image/svg+xml', '.svg')
    yield

app = FastAPI(lifespan=lifespan)


# 挂载静态文件
app.mount("/assets", StaticFiles(directory="src/frontend/dist/assets"), name="assets")

# 根路由返回 index.html
@app.get("/")
def serve_index():
    return FileResponse("src/frontend/dist/index.html")

@app.get("/favicon.ico")
def serve_ico():
    return FileResponse("src/frontend/dist/favicon.ico")

@app.get("/grape.md")
def serve_md():
    return FileResponse("src/frontend/dist/grape.md")

# 捕获所有未匹配的路由，返回 Vue 的 index.html
@app.get("/{path:path}", include_in_schema=False)
async def serve_spa(path: str):
    index_path = Path("src/frontend/dist/index.html")
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(), status_code=200)
    return {"error": "index.html not found"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    llm = CozeLLM()
    agent = ReActAgent(
        llm=llm,
        # name="grape_agent",
        # description="An agent that can query knowledge about grape cultivation and view data from vineyard areas.",
        tools=[docs_tool, api_tool, datetime_tool],
        timeout=2 * 60,
    )
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")

            handler = agent.run(input=data)
            async for ev in handler.stream_events():
                match ev:
                    case StreamEvent():
                        await manager.send_personal_message(f"0:{ev.delta}", websocket)
                    case ToolCallResultMessage():
                        await manager.send_personal_message(f"a:{ev.output}", websocket)
                    case StopSignal():
                        await manager.send_personal_message("d:=== end ===", websocket)
                    case _:
                        continue
            await handler
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
