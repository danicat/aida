import os
import random
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from dotenv import load_dotenv
# from PIL import Image

# --- Agent Definition ---
from aida.agent import root_agent
from aida.osquery_rag import rag_engine

load_dotenv()
# --- End Agent Definition ---

# --- Services and Runner Setup ---
APP_NAME = "aida"

session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    print("--- AIDA STARTUP SEQUENCE INITIATED ---")
    print("Initializing RAG Engine (loading 300M parameter model)...")
    # This might take a few seconds
    rag_engine.initialize()
    print("RAG Engine initialized successfully.")
    yield
    print("--- AIDA SHUTDOWN SEQUENCE ---")


app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Static assets ---
# Keep these for now as they are used by the JS, 
# but could also be moved to static/assets if desired later.
@app.get("/idle")
async def idle():
    return FileResponse("assets/idle.png")


@app.get("/blink")
async def blink():
    return FileResponse("assets/blink.png")


@app.get("/talk")
async def talk():
    return FileResponse("assets/talk.png")


@app.get("/think")
async def think():
    return FileResponse("assets/think.png")

@app.get("/think_blink")
async def think_blink():
    return FileResponse("assets/think_blink.png")


@app.get("/random_image")
async def random_image():
    images = os.listdir("assets")
    random_image = random.choice(images)
    return FileResponse(f"assets/{random_image}")


# --- Web Interface (HTML) ---
@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    """Serves the simple HTML chat interface."""
    return FileResponse("templates/index.html")


# --- API Endpoint for Chat Logic ---
@app.post("/chat")
async def chat_handler(request: Request):
    """Handles the chat logic, streaming the agent's response."""
    body = await request.json()
    query = body.get("query")
    user_id = "web_user"
    session_id = "web_session"

    # Ensure a session exists
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not session:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

    async def stream_generator():
        """Streams JSON-formatted events for logs and text."""
        full_response = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(role="user", parts=[Part.from_text(text=query)]),
        ):
            # Try to capture tool calls from the event
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # Check for function calls (standard Gemini/Gemma structure)
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        # Format args nicely
                        args_str = ", ".join(f"{k}='{v}'" for k, v in fc.args.items())
                        log_msg = f"EXECUTING: {fc.name}({args_str})"
                        yield json.dumps({"type": "log", "content": log_msg}) + "\n"

            # Capture final text response
            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        new_text = part.text
                        chunk = new_text[len(full_response) :]
                        if chunk:
                            yield json.dumps({"type": "text", "content": chunk}) + "\n"
                            full_response = new_text

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")


# To run this file:
# 1. Make sure you have fastapi and uvicorn installed: pip install fastapi uvicorn
# 2. Save the code as main.py
# 3. Run from your terminal: uvicorn main:app --reload
# 4. Open your browser to http://127.0.0.1:8000