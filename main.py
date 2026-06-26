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
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# --- Agent Definition ---
from aida.agent import root_agent

load_dotenv()
# --- End Agent Definition ---

# --- Services and Runner Setup ---
APP_NAME = "agents"

session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("AIDA AGENT READY.")
    yield


app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Static assets ---
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


# --- Web Interface (HTML) ---
@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    """Serves the simple HTML chat interface."""
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    return FileResponse("templates/index.html")


# --- API Endpoint for Chat Logic ---
@app.get("/config/model")
async def get_model():
    """Returns the current model selected for the agent."""
    current_model = root_agent.model
    model_id = "gemini"  # Default
    
    print(f"DEBUG: get_model current_model type: {type(current_model)}, value: {current_model}")
    if hasattr(current_model, "model_name"):
         print(f"DEBUG: current_model.model_name: {current_model.model_name}")
         if "gemini" in current_model.model_name:
              model_id = "gemini"
         elif "qwen" in current_model.model_name:
             model_id = "qwen"
         elif "gpt-oss" in current_model.model_name:
             model_id = "gpt-oss"
    elif isinstance(current_model, str):
         if "gemini" in current_model:
              model_id = "gemini"
         elif "qwen" in current_model:
             model_id = "qwen"
         elif "gpt" in current_model:
             model_id = "gpt-oss"
             
    return {"current_model": model_id}


@app.post("/config/model")
async def change_model(request: Request):
    """Changes the model selected for the agent."""
    body = await request.json()
    model_id = body.get("model_id")

    if model_id == "gemini":
        root_agent.model = "gemini-3.5-flash"
    elif model_id == "qwen":
        root_agent.model = LiteLlm(model="ollama_chat/qwen2.5")
    elif model_id == "gpt-oss":
        root_agent.model = LiteLlm(model="ollama_chat/gpt-oss")
    else:
        return {"status": "error", "error": f"Unsupported model: {model_id}"}

    # Verify model was set correctly
    current_model = root_agent.model
    m_name = current_model if isinstance(current_model, str) else current_model.model_name if hasattr(current_model, "model_name") else str(current_model)
    print(f"Changed active agent model to: {m_name}")
    return {"status": "ok", "current_model": model_id}


@app.get("/session/usage")
async def get_session_usage():
    """Returns the session token/context usage percentages."""
    user_id = "web_user"
    session_id = "web_session"

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not session:
        return {"percentage": 0, "text": "0% (0 / 1000k)"}

    # Count actual turn/message context tokens in history if available
    token_count = len(session.events) * 450  # Estimator
    percentage = min(int((token_count / 1000000) * 100), 100)
    return {"percentage": percentage, "text": f"{percentage}% ({int(token_count / 1000)}k / 1000k)"}


@app.post("/session/clear")
async def clear_session():
    """Clears the current agent chat session."""
    user_id = "web_user"
    session_id = "web_session"
    await session_service.delete_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    # Re-create cleanly
    await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    return {"status": "ok", "message": "Session history cleared successfully."}


@app.post("/chat")
async def chat_handler(request: Request):
    """Handles the chat logic, streaming the agent's response."""
    body = await request.json()
    query = body.get("query")
    user_id = "web_user"
    session_id = "web_session"

    print(f"Processing request with model: {root_agent.model}")

    # Ensure a session exists
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not session:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

    async def stream_generator():
        """Streams JSON-formatted events for logs and raw text to the frontend."""
        current_msg_id = None
        full_response = ""
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(role="user", parts=[Part.from_text(text=query)]),
        ):
            # Track message boundaries to reset the accumulator
            if hasattr(event, "message_id") and event.message_id and event.message_id != current_msg_id:
                current_msg_id = event.message_id
                full_response = ""
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
                    
                    # Check for function responses (tool output)
                    if hasattr(part, "function_response") and part.function_response:
                        fr = part.function_response
                        # Extract result if possible, otherwise use whole response
                        if isinstance(fr.response, dict) and 'result' in fr.response:
                            output_str = str(fr.response['result'])
                        else:
                            output_str = str(fr.response)
                        
                        yield json.dumps({"type": "tool_output", "content": output_str}) + "\n"

            # Capture text response incrementally
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        new_text = part.text
                        # Fallback reset if the text is shorter than accumulated (e.g., ADK event mismatch)
                        if len(new_text) < len(full_response):
                            full_response = ""
                            
                        chunk = new_text[len(full_response) :]
                        if chunk:
                            yield json.dumps({"type": "text", "content": chunk}) + "\n"
                            full_response = new_text

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")


if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist"), name="frontend")


# To run this file:
# 1. Make sure you have fastapi and uvicorn installed: pip install fastapi uvicorn
# 2. Save the code as main.py
# 3. Run from your terminal: uvicorn main:app --reload
# 4. Open your browser to http://127.0.0.1:8000