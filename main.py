import logging
import os
import platform
import socket
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import psutil
from sse_starlette.sse import EventSourceResponse

from ag_ui.core import RunAgentInput, UserMessage
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from ag_ui_adk.endpoint import _sse_stream
from aida.agent import root_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aida")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AIDA EMERGENCY DIAGNOSTIC AGENT READY.")
    yield


app = FastAPI(
    title="AIDA Emergency Diagnostic Assistant",
    lifespan=lifespan,
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Initialize ADK Agent middleware wrapper with canonical A2UI integration
adk_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="aida",
    user_id="web_user",
    use_in_memory_services=True,
    a2ui={
        "inject_a2ui_tool": True,
        "default_catalog_id": "aida_custom",
    },
)

# 2. Register AG-UI endpoints
add_adk_fastapi_endpoint(app, adk_agent, path="/api/agent")


# 3. System Status Endpoint for Fixed Header
@app.get("/api/system-status")
async def get_system_status():
    """Returns host system hardware and operating system status for the fixed header."""
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    days, hours = divmod(hours, 24)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = (
        f"{days}d {hours}h {minutes}m"
        if days > 0
        else f"{hours}h {minutes}m {seconds}s"
    )

    mem = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=None)

    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "platform": platform.platform(),
        "kernel": platform.release(),
        "arch": platform.machine(),
        "uptime": uptime_str,
        "uptime_seconds": uptime_seconds,
        "uptime_str": uptime_str,
        "health": "NOMINAL",
        "status": "ok",
        "cpu": {
            "percent": cpu_percent,
            "count": psutil.cpu_count(logical=True),
        },
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "free": mem.available,
            "percent": mem.percent,
        },
    }


# 4. Chat endpoint supporting SSE streaming with AG-UI events
@app.post("/chat")
async def chat_handler(request: Request):
    """Handles chat queries, streaming AG-UI protocol Server-Sent Events (SSE)."""
    body = await request.json()

    if "messages" in body and isinstance(body["messages"], list):
        input_data = RunAgentInput(**body)
    else:
        query = body.get("query", "")
        thread_id = body.get("thread_id") or "web_thread"
        run_id = body.get("run_id") or str(uuid.uuid4())
        input_data = RunAgentInput(
            thread_id=thread_id,
            run_id=run_id,
            state={},
            messages=[
                UserMessage(
                    id=str(uuid.uuid4()),
                    content=query,
                )
            ],
            tools=[],
        )

    return EventSourceResponse(_sse_stream(adk_agent, input_data))


# 5. Session Management endpoints
@app.post("/session/clear")
async def clear_session():
    """Clears the current agent chat session."""
    if hasattr(adk_agent, "_session_service") and adk_agent._session_service:
        try:
            sessions = await adk_agent._session_service.list_sessions(
                app_name="aida", user_id="web_user"
            )
            for s in sessions:
                await adk_agent._session_service.delete_session(
                    app_name="aida", user_id="web_user", session_id=s.id
                )
        except Exception as e:
            logger.warning(f"Error resetting sessions: {e}")
    return {"status": "ok", "message": "Session history cleared successfully."}


@app.get("/session/usage")
async def get_session_usage():
    """Returns the session token/context usage percentages."""
    return {"percentage": 0, "text": "0% (0 / 1000k)"}


# 6. Static avatar image endpoints
@app.get("/idle")
async def get_idle_avatar():
    return FileResponse("assets/idle.png")


@app.get("/blink")
async def get_blink_avatar():
    return FileResponse("assets/blink.png")


@app.get("/talk")
async def get_talk_avatar():
    return FileResponse("assets/talk.png")


@app.get("/think")
async def get_think_avatar():
    return FileResponse("assets/think.png")


@app.get("/think_blink")
async def get_think_blink_avatar():
    return FileResponse("assets/think_blink.png")


@app.get("/error")
async def get_error_avatar():
    return FileResponse("assets/error.png")


# 7. Frontend SVG & static asset helpers
@app.get("/favicon.svg")
async def get_favicon():
    if os.path.exists("frontend/dist/favicon.svg"):
        return FileResponse("frontend/dist/favicon.svg")
    return HTMLResponse("", status_code=404)


@app.get("/icons.svg")
async def get_icons():
    if os.path.exists("frontend/dist/icons.svg"):
        return FileResponse("frontend/dist/icons.svg")
    return HTMLResponse("", status_code=404)


@app.get("/assets/{file_path:path}")
async def get_assets(file_path: str):
    dist_path = os.path.join("frontend/dist/assets", file_path)
    if os.path.exists(dist_path):
        return FileResponse(dist_path)
    root_path = os.path.join("assets", file_path)
    if os.path.exists(root_path):
        return FileResponse(root_path)
    return HTMLResponse("Not Found", status_code=404)


# 8. Web Interface (HTML)
@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    """Serves the modern AIDA frontend chat interface."""
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    return HTMLResponse("<h1>AIDA Diagnostic Assistant - Build Missing</h1>", status_code=500)


# 9. Fallback mounts for static directories
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
elif os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")