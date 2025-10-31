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
