import os
import random
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
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


# --- Static assets ---
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
    return r'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emergency Diagnostic Agent</title>
        <link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; }
            :root {
                --pc98-bg: #000022;
                --pc98-fg: #d4d4d4;
                --pc98-green: #55ff55;
                --pc98-cyan: #00ffff;
                --pc98-border: #5555aa;
                --pc98-dark-gray: #222244;
                --pc98-amber: #ffb700;
            }
            body { 
                font-family: 'VT323', monospace;
                font-size: 20px;
                background-color: var(--pc98-bg);
                color: var(--pc98-fg);
                display: flex; 
                justify-content: center; 
                align-items: flex-start;
                padding-top: 50px;
                height: 100vh;
                margin: 0;
                background-image: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
                background-size: 100% 2px, 3px 100%;
            }
            #main-container {
                display: flex;
                gap: 20px;
            }
            #left-panel {
                width: 600px;
                display: flex;
                flex-direction: column;
            }
            #right-panel {
                width: 300px;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            #chat-container { 
                flex-grow: 1;
                border: 4px double var(--pc98-border);
                padding: 20px; 
                background-color: var(--pc98-bg);
                box-shadow: 0 0 15px rgba(85, 85, 170, 0.3);
            }
            #header {
                text-align: center;
                font-size: 28px;
                margin-bottom: 20px;
                color: var(--pc98-green);
                text-shadow: 0 0 8px var(--pc98-green);
                border-bottom: 2px solid var(--pc98-border);
                padding-bottom: 10px;
            }
            #messages { 
                height: 400px; 
                overflow-y: scroll; 
                border: 2px solid var(--pc98-border);
                padding: 10px; 
                margin-bottom: 15px; 
                background-color: #000011;
                scrollbar-width: thin;
                scrollbar-color: var(--pc98-border) var(--pc98-bg);
            }
            #user-input { display: flex; align-items: center; }
            #prompt-symbol {
                color: var(--pc98-green);
                margin-right: 10px;
                font-weight: bold;
            }
            #user-input input { 
                flex-grow: 1; 
                padding: 8px; 
                background-color: var(--pc98-bg);
                border: none;
                border-bottom: 2px solid var(--pc98-green);
                color: var(--pc98-green);
                font-family: 'VT323', monospace;
                font-size: 22px;
                outline: none;
            }
            #user-input input::placeholder {
                color: var(--pc98-border);
            }
            .user-message { text-align: right; color: var(--pc98-cyan); margin-bottom: 8px; }
            .agent-message { color: var(--pc98-green); margin-bottom: 8px; white-space: pre-wrap; }
            
            #avatar-window {
                width: 100%;
                height: 300px;
                border: 4px ridge var(--pc98-border);
                background-color: #000011;
                display: flex;
                justify-content: center;
                align-items: center;
                image-rendering: pixelated;
            }
            #avatar-window img {
                max-width: 100%;
                max-height: 100%;
            }
            
            #avatar-label {
                width: 100%;
                color: var(--pc98-green);
                font-size: 24px;
                text-align: center;
                text-shadow: 0 0 5px var(--pc98-green);
                border: 2px solid var(--pc98-border);
                padding: 5px;
                background-color: var(--pc98-dark-gray);
            }
            #system-log-window {
                width: 100%;
                flex-grow: 1;
                border: 4px double var(--pc98-border);
                background-color: #000011;
                padding: 10px;
                font-size: 16px;
                overflow-y: auto;
                overflow-x: hidden;
                height: 200px;
                scrollbar-width: thin;
                scrollbar-color: var(--pc98-border) #000011;
                overflow-wrap: anywhere;
            }
            .log-entry { 
                margin-bottom: 4px; 
                line-height: 1.2;
                white-space: pre-wrap;
            }
            .log-time { color: var(--pc98-cyan); margin-right: 5px; }
            .log-sys { color: var(--pc98-amber); }
        </style>
    </head>
    <body>
        <div id="main-container">
            <div id="left-panel">
                <div id="chat-container">
                    <div id="header">*** EMERGENCY DIAGNOSTIC AGENT ***</div>
                    <div id="messages"></div>
                    <form id="user-input" onsubmit="sendMessage(event)">
                        <span id="prompt-symbol">AIDA&gt;</span>
                        <input type="text" id="message-text" autocomplete="off" autofocus />
                    </form>
                </div>
            </div>
            <div id="right-panel">
                <div id="avatar-window">
                    <img src="/idle" alt="Agent Avatar" id="avatar-img">
                </div>
                <div id="avatar-label">STATUS: ONLINE</div>
                <div id="system-log-window">
                    <div id="system-log"></div>
                </div>
            </div>
        </div>
        <script>
            const messagesDiv = document.getElementById('messages');
            const messageText = document.getElementById('message-text');
            const avatarImg = document.getElementById('avatar-img');
            const avatarLabel = document.getElementById('avatar-label');
            const systemLog = document.getElementById('system-log');
            const logWindow = document.getElementById('system-log-window');

            function logActivity(message, type = 'info') {
                const now = new Date();
                const timeStr = now.toTimeString().split(' ')[0];
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.innerHTML = `<span class="log-time">[${timeStr}]</span> <span class="log-sys">${message}</span>`;
                systemLog.appendChild(entry);
                logWindow.scrollTop = logWindow.scrollHeight;
            }

            // Boot sequence simulation
            setTimeout(() => logActivity("SYSTEM STARTUP..."), 500);
            setTimeout(() => logActivity("LOADING KERNEL..."), 1200);
            setTimeout(() => logActivity("CONNECTING TO OSQUERY DAEMON..."), 2000);
            setTimeout(() => logActivity("RAG DATABASE LOADED (283 tables)."), 2800);
            setTimeout(() => logActivity("AIDA AGENT READY."), 3500);

            // Idle blinking logic
            let blinkInterval = null;
            function startBlinking() {
                if (blinkInterval) return;
                // Blink every 4-8 seconds randomly (slower)
                blinkInterval = setTimeout(function blink() {
                    avatarImg.src = '/blink';
                    setTimeout(() => {
                        // Only switch back to idle if we are still in ONLINE state
                        if (avatarLabel.textContent === "STATUS: ONLINE") {
                             avatarImg.src = '/idle';
                        }
                    }, 300); // Eyes closed for 300ms
                    blinkInterval = setTimeout(blink, Math.random() * 4000 + 4000);
                }, 4000);
            }

            function stopBlinking() {
                if (blinkInterval) {
                    clearTimeout(blinkInterval);
                    blinkInterval = null;
                }
            }

            // Start blinking initially
            startBlinking();

            async function sendMessage(event) {
                event.preventDefault();
                const query = messageText.value;
                if (!query) return;

                // Display user message
                const userMsgDiv = document.createElement('div');
                userMsgDiv.className = 'user-message';
                userMsgDiv.textContent = `> ${query}`;
                messagesDiv.appendChild(userMsgDiv);
                messageText.value = '';
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                logActivity(`INPUT RECEIVED: "${query.substring(0, 20)}${query.length > 20 ? '...' : ''}"`);

                // Create a container for the agent's response
                const agentMsgDiv = document.createElement('div');
                agentMsgDiv.className = 'agent-message';
                messagesDiv.appendChild(agentMsgDiv);

                stopBlinking();
                avatarImg.src = '/think'; // Set to thinking pose
                avatarLabel.textContent = "STATUS: THINKING";
                avatarLabel.style.color = "var(--pc98-cyan)";
                logActivity("AGENT STATUS: THINKING...");

                // Thinking animation
                let thinkBlinkInterval = setInterval(() => {
                     avatarImg.src = '/think_blink';
                     setTimeout(() => {
                         if (avatarLabel.textContent === "STATUS: THINKING") {
                             avatarImg.src = '/think';
                         }
                     }, 300);
                }, 3500);

                try {
                    // Stream agent response
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = "";
                    let isStreaming = true;

                    let animationInterval = null;

                    function startTalkingAnimation() {
                        if (animationInterval) return;
                        clearInterval(thinkBlinkInterval); // Stop thinking animation
                        let toggle = false;
                        avatarImg.src = '/talk';
                        avatarLabel.textContent = "STATUS: RESPONDING";
                        avatarLabel.style.color = "var(--pc98-green)";
                        // logActivity("AGENT STATUS: RESPONDING..."); 
                        animationInterval = setInterval(() => {
                            toggle = !toggle;
                            avatarImg.src = toggle ? '/talk' : '/idle';
                        }, 150);
                    }

                    function stopAnimation() {
                        clearInterval(thinkBlinkInterval); // Ensure stopped
                        if (animationInterval) {
                            clearInterval(animationInterval);
                            animationInterval = null;
                        }
                        avatarImg.src = '/idle';
                        avatarLabel.textContent = "STATUS: ONLINE";
                        avatarLabel.style.color = "var(--pc98-green)";
                        logActivity("AGENT STATUS: IDLE.");
                        startBlinking();
                    }

                    // Asynchronously read from the stream
                    (async () => {
                        while (true) {
                            const { value, done } = await reader.read();
                            if (done) {
                                stopAnimation();
                                break;
                            }
                            buffer += decoder.decode(value, { stream: true });
                            
                            // Process complete lines from buffer
                            let lineEnd;
                            while ((lineEnd = buffer.indexOf('\n')) !== -1) {
                                const line = buffer.substring(0, lineEnd).trim();
                                buffer = buffer.substring(lineEnd + 1);
                                if (line) {
                                    try {
                                        const data = JSON.parse(line);
                                        if (data.type === 'log') {
                                            logActivity(data.content);
                                        } else if (data.type === 'text') {
                                            startTalkingAnimation();
                                            // Append text character by character for retro feel
                                            for (const char of data.content) {
                                                agentMsgDiv.textContent += char;
                                                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                                                await new Promise(r => setTimeout(r, 10)); // Tiny delay for typing effect
                                            }
                                        }
                                    } catch (e) {
                                        console.error("Error parsing JSON line:", line, e);
                                    }
                                }
                            }
                        }
                    })();

                } catch (e) {
                    clearInterval(thinkBlinkInterval); // Stop thinking animation on error
                    avatarImg.src = '/idle';
                    avatarLabel.textContent = "STATUS: ERROR";
                    avatarLabel.style.color = "red";
                    agentMsgDiv.textContent = "ERROR: CONNECTION LOST";
                    logActivity("ERROR: CONNECTION LOST!", "error");
                    startBlinking();
                }
            }
        </script>
    </body>
    </html>
    '''


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
