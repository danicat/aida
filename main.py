import os
import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from dotenv import load_dotenv
# from PIL import Image

# --- Agent Definition ---
from aida.agent import root_agent

load_dotenv()
# --- End Agent Definition ---

# --- Services and Runner Setup ---
APP_NAME="aida"

session_service = InMemorySessionService()
runner = Runner(
    app_name=APP_NAME, agent=root_agent, session_service=session_service
)
app = FastAPI()

# --- Static assets ---
@app.get("/idle")
async def idle():
    return FileResponse("assets/idle.png")

@app.get("/talk")
async def talk():
    return FileResponse("assets/talk.png")

@app.get("/think")
async def think():
    return FileResponse("assets/thinking.png")

@app.get("/random_image")
async def random_image():
    images = os.listdir("assets")
    random_image = random.choice(images)
    return FileResponse(f"assets/{random_image}")


# --- Web Interface (HTML) ---
@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    """Serves the simple HTML chat interface."""
    return r"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emergency Diagnostic Agent</title>
        <link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
        <style>
            :root {
                --pc98-bg: #000022;
                --pc98-fg: #d4d4d4;
                --pc98-green: #55ff55;
                --pc98-cyan: #00ffff;
                --pc98-border: #5555aa;
                --pc98-dark-gray: #222244;
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
            #chat-container { 
                width: 600px; 
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
            #avatar-container {
                width: 220px;
                text-align: center;
            }
            #avatar-window {
                width: 200px;
                height: 200px;
                border: 4px ridge var(--pc98-border);
                background-color: #000011;
                margin: 0 auto 15px;
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
                color: var(--pc98-green);
                font-size: 24px;
                text-shadow: 0 0 5px var(--pc98-green);
                border: 2px solid var(--pc98-border);
                padding: 5px;
                background-color: var(--pc98-dark-gray);
            }
            /* Blinking cursor effect for input */
            @keyframes blink { 50% { opacity: 0; } }
            #user-input input:focus + #cursor {
                animation: blink 1s step-end infinite;
            }
        </style>
    </head>
    <body>
        <div id="main-container">
            <div id="chat-container">
                <div id="header">*** EMERGENCY DIAGNOSTIC AGENT ***</div>
                <div id="messages"></div>
                <form id="user-input" onsubmit="sendMessage(event)">
                    <span id="prompt-symbol">AIDA&gt;</span>
                    <input type="text" id="message-text" autocomplete="off" autofocus />
                </form>
            </div>
            <div id="avatar-container">
                <div id="avatar-window">
                    <img src="/idle" alt="Agent Avatar" id="avatar-img">
                </div>
                <div id="avatar-label">STATUS: ONLINE</div>
            </div>
        </div>
        <script>
            const messagesDiv = document.getElementById('messages');
            const messageText = document.getElementById('message-text');
            const avatarImg = document.getElementById('avatar-img');
            const avatarLabel = document.getElementById('avatar-label');

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

                // Create a container for the agent's response
                const agentMsgDiv = document.createElement('div');
                agentMsgDiv.className = 'agent-message';
                messagesDiv.appendChild(agentMsgDiv);

                avatarImg.src = '/think'; // Set to thinking pose
                avatarLabel.textContent = "STATUS: THINKING";
                avatarLabel.style.color = "var(--pc98-cyan)";

                try {
                    // Stream agent response
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let wordQueue = [];
                    let isStreaming = true;

                    // Asynchronously read from the stream and populate the word queue
                    (async () => {
                        while (true) {
                            const { value, done } = await reader.read();
                            if (done) {
                                isStreaming = false;
                                break;
                            }
                            const chunk = decoder.decode(value, { stream: true });
                            // Split by characters for a more retro typing feel, or keep words if preferred
                            wordQueue.push(...chunk.split('')); 
                        }
                    })();

                    let animationInterval = null;

                    function startAnimation() {
                        if (animationInterval) return;
                        let toggle = false;
                        avatarImg.src = '/talk';
                        avatarLabel.textContent = "STATUS: RESPONDING";
                        avatarLabel.style.color = "var(--pc98-green)";
                        animationInterval = setInterval(() => {
                            toggle = !toggle;
                            avatarImg.src = toggle ? '/talk' : '/idle';
                        }, 150);
                    }

                    function stopAnimation() {
                        if (animationInterval) {
                            clearInterval(animationInterval);
                            animationInterval = null;
                        }
                        avatarImg.src = '/idle';
                        avatarLabel.textContent = "STATUS: ONLINE";
                        avatarLabel.style.color = "var(--pc98-green)";
                    }

                    function render() {
                        if (wordQueue.length > 0) {
                            startAnimation();
                            const char = wordQueue.shift();
                            agentMsgDiv.textContent += char;
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                            setTimeout(render, 20); // Slightly faster character-based typing
                        } else if (isStreaming) {
                            setTimeout(render, 50);
                        } else {
                            stopAnimation();
                        }
                    }

                    render();
                } catch (e) {
                    avatarImg.src = '/idle';
                    avatarLabel.textContent = "STATUS: ERROR";
                    avatarLabel.style.color = "red";
                    agentMsgDiv.textContent = "ERROR: CONNECTION LOST";
                }
            }
        </script>
    </body>
    </html>
    """


# --- API Endpoint for Chat Logic ---
@app.post("/chat")
async def chat_handler(request: Request):
    """Handles the chat logic, streaming the agent's response."""
    body = await request.json()
    query = body.get("query")
    user_id = "web_user"
    session_id = "web_session" # In a real app, you'd manage sessions per user

    # Ensure a session exists
    session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    if not session:
        session = await session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)

    async def stream_generator():
        """Streams the agent's final text response chunks."""
        full_response = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(role="user", parts=[Part.from_text(text=query)]),
        ):
            if event.is_final_response() and event.content and event.content.parts[0].text:
                new_text = event.content.parts[0].text
                # Yield only the new part of the text
                yield new_text[len(full_response):]
                full_response = new_text

    return StreamingResponse(stream_generator(), media_type="text/plain")

# To run this file:
# 1. Make sure you have fastapi and uvicorn installed: pip install fastapi uvicorn
# 2. Save the code as main.py
# 3. Run from your terminal: uvicorn main:app --reload
# 4. Open your browser to http://127.0.0.1:8000
