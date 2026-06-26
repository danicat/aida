import { LitElement, html, css } from 'lit';
import { customElement, state, query } from 'lit/decorators.js';
import { MessageProcessor } from '@a2ui/web_core/v0_9';
import { basicCatalog, Context } from '@a2ui/lit/v0_9';
import { aidaCustomCatalog } from './aida-catalog/index.js';
import { provide } from '@lit/context';
import { renderMarkdown } from '@a2ui/markdown-it';
import '@a2ui/lit/v0_9'; // Registers the <a2ui-surface> component

class A2uiStreamParser {
    private buffer = '';
    private state: 'text' | 'a2ui' = 'text';

    onText: (text: string) => void;
    onA2ui: (jsonStr: string) => void;

    constructor(onText: (text: string) => void, onA2ui: (jsonStr: string) => void) {
        this.onText = onText;
        this.onA2ui = onA2ui;
    }

    append(chunk: string) {
        this.buffer += chunk;
        this.processBuffer();
    }

    private processBuffer() {
        let changed = true;
        while (changed) {
            changed = false;
            if (this.state === 'text') {
                const openTagIndex = this.buffer.indexOf('<a2ui>');
                if (openTagIndex !== -1) {
                    const textPart = this.buffer.substring(0, openTagIndex);
                    if (textPart) {
                        this.onText(textPart);
                    }
                    this.buffer = this.buffer.substring(openTagIndex + '<a2ui>'.length);
                    this.state = 'a2ui';
                    changed = true;
                } else {
                    let splitIndex = this.buffer.length;
                    for (let i = 1; i < 6; i++) {
                        if (this.buffer.endsWith('<a2ui>'.substring(0, i))) {
                            splitIndex = this.buffer.length - i;
                            break;
                        }
                    }
                    const textPart = this.buffer.substring(0, splitIndex);
                    if (textPart) {
                        this.onText(textPart);
                        this.buffer = this.buffer.substring(splitIndex);
                    }
                }
            } else if (this.state === 'a2ui') {
                const closeTagIndex = this.buffer.indexOf('</a2ui>');
                if (closeTagIndex !== -1) {
                    const jsonPart = this.buffer.substring(0, closeTagIndex);
                    if (jsonPart) {
                        const cleanJsonStr = jsonPart.replace(/```[a-zA-Z]*\n?|```/g, '').trim();
                        this.onA2ui(cleanJsonStr);
                    }
                    this.buffer = this.buffer.substring(closeTagIndex + '</a2ui>'.length);
                    this.state = 'text';
                    changed = true;
                }
            }
        }
    }

    end() {
        if (this.state === 'text' && this.buffer) {
            this.onText(this.buffer);
            this.buffer = '';
        }
    }
}
interface ChatMessage {
  role: 'user' | 'agent' | 'system';
  content: string;
}

@customElement('aida-chat')
export class AidaChat extends LitElement {
  static styles = css`
    :host {
      display: block;
      width: 1200px;
      height: 850px;
      max-width: 95vw;
      max-height: 95vh;
      font-family: 'VT323', monospace;
      font-size: 24px;
      color: var(--pc98-fg);
    }
    
    #main-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        width: 100%;
        height: 100%;
    }

    /* Boot / Greeting Layout (Centered Cozy) */
    #boot-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        width: 100%;
        height: 100%;
        border: 4px double var(--pc98-border);
        padding: 40px;
        background-color: var(--pc98-bg);
        box-shadow: 0 0 20px rgba(85, 85, 170, 0.4);
    }
    #boot-header {
        text-align: center;
        font-size: 38px;
        color: var(--pc98-green);
        text-shadow: 0 0 10px var(--pc98-green);
        border-bottom: 2px solid var(--pc98-border);
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    #boot-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 40px;
        flex-grow: 1;
        margin-bottom: 30px;
    }
    #boot-avatar-pane {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 15px;
    }
    .boot-avatar {
        width: 256px !important;
        height: 256px !important;
    }
    #boot-bubble {
        flex: 1;
        max-width: 600px;
        border: 4px ridge var(--pc98-border);
        background-color: #000011;
        padding: 25px;
        position: relative;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    #boot-bubble::before {
        content: '';
        position: absolute;
        left: -15px;
        top: 50px;
        border-width: 10px 15px 10px 0;
        border-style: solid;
        border-color: transparent var(--pc98-border) transparent transparent;
    }
    .bubble-text {
        font-size: 28px;
        color: var(--pc98-green);
        line-height: 1.4;
    }

    /* Single-Column Full Canvas Layout (Active Workspace) */
    #canvas-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        width: 100%;
        height: 100%;
        border: 4px double var(--pc98-border);
        padding: 20px;
        background-color: var(--pc98-bg);
        box-shadow: 0 0 20px rgba(85, 85, 170, 0.4);
    }
    #canvas-viewport {
        flex-grow: 1;
        min-height: 0;
        overflow-y: auto;
        border: 2px solid var(--pc98-border);
        background-color: #000011;
        padding: 15px;
        margin-bottom: 15px;
        scrollbar-width: thin;
        scrollbar-color: var(--pc98-border) #000011;
    }
    .canvas-title {
        color: var(--pc98-cyan);
        font-size: 28px;
        text-align: center;
        border-bottom: 2px solid var(--pc98-border);
        padding-bottom: 5px;
        text-shadow: 0 0 8px var(--pc98-cyan);
    }

    /* Canvas Surfaces */
    .canvas-surface-container {
        margin-bottom: 15px;
        border: 2px solid var(--pc98-border);
        background-color: var(--pc98-bg);
    }
    .canvas-surface-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: var(--pc98-dark-gray);
        border-bottom: 2px solid var(--pc98-border);
        padding: 4px 10px;
        color: var(--pc98-green);
        font-size: 18px;
    }
    .canvas-surface-header .close-btn {
        background: transparent;
        border: none;
        color: var(--pc98-red);
        font-family: inherit;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
    }
    .canvas-surface-header .close-btn:hover {
        color: #fff;
    }
    .canvas-surface-body {
        padding: 12px;
    }

    /* Input elements */
    #user-input { display: flex; align-items: center; }
    #prompt-symbol {
        color: var(--pc98-green);
        margin-right: 10px;
        font-weight: bold;
        font-size: 24px;
    }
    #user-input input {
        flex-grow: 1;
        padding: 8px;
        background-color: var(--pc98-bg);
        border: none;
        border-bottom: 2px solid var(--pc98-green);
        color: var(--pc98-green);
        font-family: 'VT323', monospace;
        font-size: 24px;
        outline: none;
        min-width: 0;
    }
    #user-input input::placeholder {
        color: var(--pc98-border);
    }
    
    /* Standard messages */
    .user-message { text-align: right; color: var(--pc98-cyan); margin-bottom: 8px; font-size: 24px; }
    .agent-message { color: var(--pc98-green); margin-bottom: 8px; font-size: 24px; }
    .agent-message p { margin-top: 0; margin-bottom: 5px; }
    .agent-message code { 
        font-family: 'VT323', monospace; 
        font-size: inherit; 
        background-color: var(--pc98-dark-gray); 
        padding: 2px 4px; 
        color: var(--pc98-cyan);
        word-break: break-all; 
    }
    .agent-message pre { 
        font-family: 'VT323', monospace; 
        font-size: inherit; 
        background-color: #000011; 
        padding: 10px; 
        overflow-x: auto; 
        border: 1px solid var(--pc98-border);
        max-width: 100%; 
        white-space: pre-wrap; 
    }
    .agent-message pre code {
        background-color: transparent;
        padding: 0;
        color: inherit;
    }

    /* Common panel overrides */
    .panel {
        display: flex;
        flex-direction: column;
        gap: 10px;
        border: 2px solid var(--pc98-border);
        padding: 10px;
        background-color: var(--pc98-dark-gray);
        margin-top: 10px;
    }
    .panel-title {
        color: var(--pc98-green);
        font-size: 20px;
        margin-bottom: 5px;
        text-align: center;
    }
    #model-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    #model-row button {
        flex: 1;
        font-size: 18px;
    }
    .panel button {
        padding: 0;
        height: 40px;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: var(--pc98-bg);
        color: var(--pc98-green);
        border: 2px solid var(--pc98-border);
        font-family: 'VT323', monospace;
        font-size: 20px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .panel button:hover, .panel button.active {
        background-color: var(--pc98-green);
        color: var(--pc98-bg);
    }
    #debug-toggle.active {
        background-color: var(--pc98-green);
        color: var(--pc98-bg);
    }

    /* Logs & memory meters in Canvas */
    #system-log-window {
        width: 100%;
        height: 180px;
        flex-shrink: 0;
        border: 2px solid var(--pc98-border);
        background-color: #000011;
        padding: 10px;
        font-size: 18px;
        overflow-y: auto;
        overflow-x: hidden;
        scrollbar-width: thin;
        scrollbar-color: var(--pc98-border) #000011;
        overflow-wrap: anywhere;
        margin-top: 10px;
    }
    .log-entry { 
        margin-bottom: 4px; 
        line-height: 1.2;
        white-space: pre-wrap;
    }
    .log-time { color: var(--pc98-cyan); margin-right: 5px; }
    .log-sys { color: var(--pc98-amber); }

    /* Memory / context usage meter */
    #memory-row {
        display: flex;
        gap: 10px;
        height: 35px;
    }
    #memory-row button {
        flex: 0 0 30%;
        height: 100%;
    }
    #context-bar-container {
        flex: 1;
        height: 100%;
        background-color: #000011;
        border: 1px solid var(--pc98-border);
        padding: 0; 
        position: relative;
    }
    #context-bar {
        width: 0%;
        height: 100%;
        background-color: var(--pc98-green);
        transition: width 0.5s ease, background-color 0.5s ease;
        position: absolute;
        top: 0;
        left: 0;
        z-index: 0;
    }
    #context-label {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1;
        color: #fff;
        text-shadow: 1px 1px 2px #000;
        font-size: 18px;
        margin-bottom: 0;
    }

    #avatar-window {
        border: 4px ridge var(--pc98-border);
        background-color: #000011;
        display: flex;
        justify-content: center;
        align-items: center;
        image-rendering: pixelated;
    }
    #avatar-window img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    #avatar-label {
        width: 100%;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        border: 3px solid var(--pc98-border);
        height: 39px; /* Reduced by 25% from 52px */
        background-color: var(--pc98-dark-gray);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 8px;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.5);
    }

    #jrpg-bubble {
        position: relative;
        height: 180px;
        display: flex;
        flex-direction: column;
    }
    #jrpg-bubble strong, #jrpg-bubble b {
        font-weight: bold;
        font-size: inherit; /* Prevent bold from rendering larger */
        color: var(--pc98-cyan); /* Highlight with retro cyan */
    }
    .bubble-text {
        font-size: 22px;
        color: var(--pc98-green);
        line-height: 1.3;
        flex: 1;
        overflow-y: auto;
        padding-right: 5px;
        scrollbar-width: thin;
        scrollbar-color: var(--pc98-border) #000000;
    }
    .bubble-text::-webkit-scrollbar {
        width: 6px;
    }
    .bubble-text::-webkit-scrollbar-track {
        background: #000000;
    }
    .bubble-text::-webkit-scrollbar-thumb {
        background: var(--pc98-border);
    }
    #jrpg-bubble p {
        margin-top: 0;
        margin-bottom: 8px;
    }
    #jrpg-bubble ul, #jrpg-bubble ol {
        margin-top: 0;
        margin-bottom: 8px;
        padding-left: 20px;
    }
    #jrpg-bubble li {
        margin-bottom: 4px;
    }
    #jrpg-bubble::before {
        content: '';
        position: absolute;
        left: -15px;
        top: 40px;
        border-width: 10px 15px 10px 0;
        border-style: solid;
        border-color: transparent var(--pc98-border) transparent transparent;
        z-index: 10;
    }
    #jrpg-bubble::after {
        content: '';
        position: absolute;
        left: -11px;
        top: 40px;
        border-width: 10px 15px 10px 0;
        border-style: solid;
        border-color: transparent #000000 transparent transparent;
        z-index: 11;
    }

    .glowing-dot {
        display: inline-block;
        width: 14px;
        height: 14px;
        background-color: var(--pc98-green);
        border-radius: 50%;
        margin-right: 12px;
        box-shadow: 0 0 10px var(--pc98-green);
        animation: pulse 1.5s infinite;
    }
    .glowing-dot.error {
        background-color: var(--pc98-red);
        box-shadow: 0 0 8px var(--pc98-red);
    }
    .glowing-dot.warning {
        background-color: var(--pc98-amber);
        box-shadow: 0 0 8px var(--pc98-amber);
    }
    .glowing-dot.thinking {
        background-color: var(--pc98-cyan);
        box-shadow: 0 0 8px var(--pc98-cyan);
    }

    .loading-msg {
       color: var(--pc98-green);
       font-style: italic;
    }
    
    /* Global basic overrides missing from component scope */
    button {
       outline: none;
    }
    h1, h2, h3, h4, h5, h6 {
       color: var(--pc98-cyan);
       text-shadow: 0 0 5px var(--pc98-cyan);
       margin: 10px 0;
       border-bottom: 1px dashed var(--pc98-border);
       padding-bottom: 5px;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.6; }
    }
  `;

  // state
  @provide({ context: Context.markdown })
  markdownRenderer = renderMarkdown;

  @state() private messages: ChatMessage[] = [];
  @state() private logs: {time: string, sys: boolean, content: string, type: 'normal'|'error'}[] = [];
  @state() private avatarState: 'idle' | 'think' | 'think_blink' | 'talk' | 'error' | 'blink' = 'idle';
  @state() private avatarLabelText = 'STATUS: ONLINE';
  @state() private avatarLabelColor = 'var(--pc98-green)';
  @state() private debugMode = false;
  @state() activeModel = 'gemini';
  @state() contextPercentage = 0;
  @state() contextText = '0% (0 / 1000k)';
  @state() private activeSurfaces: Map<string, any> = new Map();
  @state() private showLogs = false;
  @state() private showModelPanel = false;
  @state() private showMemoryPanel = false;
  @state() private dialogueText = 'Please state the nature of the diagnostic emergency.';
  @state() private currentTask: string | null = null;
  @state() private cacheBuster = Date.now();
  
  @query('#message-text') private inputEl!: HTMLInputElement;
  @query('#system-log-window') private logsContainer!: HTMLElement;
  
  private animationInterval: any = null;
  private thinkBlinkInterval: any = null;
  private processedA2uiBlocks: Set<string> = new Set();

  private processor!: MessageProcessor<any>;

  private initProcessor() {
    this.processor = new MessageProcessor([basicCatalog, aidaCustomCatalog], (action: any) => {
      let textToSend = "";
      if (typeof action === 'string') textToSend = action;
      else if (action && action.name) textToSend = action.name;
      else textToSend = JSON.stringify(action);
      this.sendMessage(textToSend);
    });

    this.processor.onSurfaceCreated((surface: any) => {
      this.activeSurfaces = new Map(this.activeSurfaces.set(surface.id, surface));
      
      // Force Lit re-renders when components are created, deleted, or properties are updated
      surface.componentsModel.onCreated.subscribe((comp: any) => {
          this.activeSurfaces = new Map(this.activeSurfaces);
          if (comp && comp.onUpdated) {
              comp.onUpdated.subscribe(() => {
                  this.activeSurfaces = new Map(this.activeSurfaces);
              });
          }
      });
      surface.componentsModel.onDeleted.subscribe(() => {
          this.activeSurfaces = new Map(this.activeSurfaces);
      });
    });

    this.processor.onSurfaceDeleted((surfaceId: any) => {
      const next = new Map(this.activeSurfaces);
      next.delete(surfaceId);
      this.activeSurfaces = next;
    });
  }

  constructor() {
    super();
    this.messages = [
      { role: 'agent', content: 'Please state the nature of the diagnostic emergency.' }
    ];
    this.logActivity('AIDA AGENT READY.', true);
    this.initProcessor();
  }

  willUpdate(changedProperties: Map<PropertyKey, unknown>) {
    if (changedProperties.has('avatarState')) {
        this.cacheBuster = Date.now();
    }
  }

  connectedCallback() {
    super.connectedCallback();

    // Handle JRPG dialogue updates dispatched from AIDA's A2UI components
    this.addEventListener('aida-dialogue-rendered', (e: any) => {
        const props = e.detail;
        this.dialogueText = props.text;
        
        // Map avatarUrl to state unambiguously using endsWith
        const url = (props.avatarUrl || "").toLowerCase();
        if (url.endsWith('talk') || url.endsWith('talk.png')) this.avatarState = 'talk';
        else if (url.endsWith('think_blink') || url.endsWith('think_blink.png')) this.avatarState = 'think_blink';
        else if (url.endsWith('think') || url.endsWith('think.png')) this.avatarState = 'think';
        else if (url.endsWith('error') || url.endsWith('error.png')) this.avatarState = 'error';
        else if (url.endsWith('blink') || url.endsWith('blink.png')) this.avatarState = 'blink';
        else this.avatarState = 'idle';

        if (props.type === 'error') {
            this.avatarLabelText = 'STATUS: ERROR';
            this.avatarLabelColor = 'var(--pc98-red)';
        } else if (props.type === 'warning') {
            this.avatarLabelText = 'STATUS: WARNING';
            this.avatarLabelColor = 'var(--pc98-amber)';
        } else {
            this.avatarLabelText = 'STATUS: ONLINE';
            this.avatarLabelColor = 'var(--pc98-green)';
        }
    });

    this.startBlinking();
    this.updateContextMeter();

    const params = new URLSearchParams(window.location.search);
    const queryParam = params.get('query');
    if (queryParam) {
        setTimeout(() => {
            this.sendMessage(queryParam);
        }, 1000);
    }
  }
  
  disconnectedCallback() {
    super.disconnectedCallback();
    this.stopAnimation();
    this.stopBlinking();
  }

  private logActivity(message: string, isSystem = false, type: 'normal'|'error' = 'normal') {
      const now = new Date();
      const timeStr = `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}]`;
      this.logs = [...this.logs, { time: timeStr, sys: isSystem, content: message, type }];
      setTimeout(() => {
        if (this.logsContainer) this.logsContainer.scrollTop = this.logsContainer.scrollHeight;
      }, 50);
  }

  private async updateContextMeter() {
      try {
          const response = await fetch('/session/usage');
          const data = await response.json();
          if (data.status === 'ok') {
              let percentage = (data.tokens_used / data.max_tokens) * 100;
              this.contextPercentage = Math.min(percentage, 100);
              this.contextText = `${percentage.toFixed(1)}% (${data.tokens_used} / ${data.max_tokens})`;
          }
      } catch (e) {
          console.error("Failed to update context meter", e);
      }
  }

  private startBlinking() {
      this.stopBlinking();
      const scheduleNextBlink = () => {
          const randomDelay = 2000 + Math.random() * 4000; // Random interval between 2s and 6s
          this.thinkBlinkInterval = setTimeout(() => {
              if (this.avatarState === 'idle') {
                  this.avatarState = 'blink';
                  setTimeout(() => {
                      if (this.avatarState === 'blink') {
                          this.avatarState = 'idle';
                      }
                      scheduleNextBlink();
                  }, 150);
              } else {
                  scheduleNextBlink();
              }
          }, randomDelay);
      };
      scheduleNextBlink();
  }

  private stopBlinking() {
      if (this.thinkBlinkInterval) {
          clearTimeout(this.thinkBlinkInterval);
          clearInterval(this.thinkBlinkInterval); // Also clear in case any interval is running
          this.thinkBlinkInterval = null;
      }
  }

  private startTalkingAnimation() {
      if (this.animationInterval) return;
      this.stopBlinking();
      let toggle = false;
      this.avatarState = 'talk';
      this.avatarLabelText = "STATUS: RESPONDING";
      this.avatarLabelColor = "var(--pc98-green)";
      this.animationInterval = setInterval(() => {
          toggle = !toggle;
          this.avatarState = toggle ? 'talk' : 'idle';
      }, 150);
  }

  private stopAnimation() {
      this.stopBlinking();
      if (this.animationInterval) {
          clearInterval(this.animationInterval);
          this.animationInterval = null;
      }
      this.avatarState = 'idle';
      this.avatarLabelText = "STATUS: ONLINE";
      this.avatarLabelColor = "var(--pc98-green)";
      this.currentTask = null; // Clear active task on turn end!
      this.logActivity("AGENT STATUS: IDLE.");
      this.startBlinking();
  }

  private async handleCommand(query: string): Promise<boolean> {
      if (query.startsWith('/model ')) {
          const modelId = query.split(' ')[1];
          this.logActivity(`COMMAND: SWITCHING MODEL TO '${modelId}'...`);
          try {
              const response = await fetch('/config/model', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ model_id: modelId })
              });
              const data = await response.json();
              if (data.status === 'ok') {
                  this.logActivity(`SUCCESS: MODEL SWITCHED TO ${data.current_model}`);
                  this.activeModel = modelId;
                  this.messages = [...this.messages, { role: 'system', content: '[SYSTEM] Model switched successfully.' }];
                  this.updateContextMeter();
              } else {
                  this.logActivity(`ERROR: ${data.error}`, false, 'error');
                  this.messages = [...this.messages, { role: 'system', content: `[SYSTEM] Error: ${data.error}` }];
              }
          } catch (e) {
              this.logActivity(`ERROR: FAILED TO SWITCH MODEL`, false, 'error');
          }
          return true;
      }

      if (query === '/clear') {
          this.logActivity("COMMAND: CLEARING SESSION MEMORY...");
          try {
               const response = await fetch('/session/clear', { method: 'POST' });
               const data = await response.json();
               this.logActivity(`SUCCESS: ${data.message}`);
               this.messages = []; // Clear chat window
               this.processedA2uiBlocks.clear(); // Clear processed A2UI blocks
               this.updateContextMeter(); 
          } catch (e) {
               this.logActivity("ERROR: FAILED TO CLEAR SESSION", false, 'error');
          }
          return true;
      }

      if (query === '/debug') {
          this.logActivity("COMMAND: TOGGLING DEBUG MODE...");
          this.debugMode = !this.debugMode;
          return true;
      }

      if (query === '/logs') {
          this.showLogs = !this.showLogs;
          this.logActivity(`COMMAND: TOGGLED SYSTEM LOGS: ${this.showLogs ? 'VISIBLE' : 'HIDDEN'}`);
          return true;
      }

      if (query === '/model') {
          this.showModelPanel = !this.showModelPanel;
          this.logActivity(`COMMAND: TOGGLED MODEL PANEL: ${this.showModelPanel ? 'VISIBLE' : 'HIDDEN'}`);
          return true;
      }

      if (query === '/memory') {
          this.showMemoryPanel = !this.showMemoryPanel;
          this.logActivity(`COMMAND: TOGGLED MEMORY PANEL: ${this.showMemoryPanel ? 'VISIBLE' : 'HIDDEN'}`);
          return true;
      }

      return false;
  }

  private getTaskSummary(text: string): string {
      const query = text.toLowerCase().trim();
      if (query.includes('cpu') || query.includes('core')) return 'Analyzing CPU Core Utilization...';
      if (query.includes('memory') || query.includes('ram') || query.includes('swap')) return 'Analyzing System Memory Allocation...';
      if (query.includes('disk') || query.includes('volume') || query.includes('space') || query.includes('storage')) return 'Analyzing Disk Storage Volumes...';
      if (query.includes('network') || query.includes('interface') || query.includes('rx') || query.includes('tx')) return 'Monitoring Network Interface Throughput...';
      if (query.includes('process') || query.includes('ps')) return 'Querying Active System Processes...';
      if (query.includes('log') || query.includes('syslog') || query.includes('error')) return 'Querying System Diagnostic Logs...';
      if (query.includes('table') || query.includes('schema')) return 'Searching System Schema Tables...';
      return 'Analyzing System Diagnostics...';
  }

  private async sendMessage(text: string) {
      if (!text.trim()) return;

      this.currentTask = this.getTaskSummary(text);

      this.messages = [...this.messages, { role: 'user', content: `> ${text}` }];
      if (this.inputEl) this.inputEl.value = '';

      if (await this.handleCommand(text)) {
          this.currentTask = null;
          return;
      }

      // Reset A2UI processor state for a fresh, clean turn, accumulating surfaces
      this.processedA2uiBlocks.clear();

      this.logActivity(`INPUT RECEIVED: "${text.substring(0, 20)}${text.length > 20 ? '...' : ''}"`);

      this.stopBlinking();
      this.avatarState = 'think';
      this.avatarLabelText = "STATUS: THINKING";
      this.avatarLabelColor = "var(--pc98-cyan)";
      this.dialogueText = "";
      this.logActivity("AGENT STATUS: THINKING...");

      this.thinkBlinkInterval = setInterval(() => {
          this.avatarState = 'think_blink';
          setTimeout(() => {
              if (this.avatarLabelText === "STATUS: THINKING") {
                  this.avatarState = 'think';
              }
          }, 300);
      }, 3500);

      try {
          const response = await fetch('/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ query: text })
          });

          const reader = response.body?.getReader();
          if (!reader) throw new Error("No reader");
          const decoder = new TextDecoder();
          let buffer = "";
          let fullMarkdown = "";

          let currentAgentMessageIndex = this.messages.length;
          this.messages = [...this.messages, { role: 'agent', content: 'Receiving transmission...' }];

          const parser = new A2uiStreamParser(
              (textChunk) => {
                  this.dialogueText += textChunk;
              },
              (jsonStr) => {
                  if (!this.processedA2uiBlocks.has(jsonStr)) {
                      this.processedA2uiBlocks.add(jsonStr);
                      try {
                          const parsed = JSON.parse(jsonStr);
                          this.processor.processMessages(parsed);
                      } catch (e) {
                          console.error("Error parsing client-side A2UI JSON:", e, jsonStr);
                      }
                  }
              }
          );

          while (true) {
              const { value, done } = await reader.read();
              if (done) {
                  parser.end();
                  this.stopAnimation();
                  this.updateContextMeter();
                  break;
              }
              buffer += decoder.decode(value, { stream: true });
              
              let lineEnd;
              while ((lineEnd = buffer.indexOf('\n')) !== -1) {
                  const line = buffer.substring(0, lineEnd).trim();
                  buffer = buffer.substring(lineEnd + 1);
                  if (line) {
                      try {
                          const data = JSON.parse(line);
                          if (data.type === 'log') {
                              this.logActivity(data.content);
                              if (data.content.includes("EXECUTING: run_osquery")) {
                                  this.currentTask = "Executing osquery Diagnostic Database Query...";
                              } else if (data.content.includes("EXECUTING: search_query_library")) {
                                  this.currentTask = "Searching Query Library RAG database...";
                              } else if (data.content.includes("EXECUTING: discover_schema")) {
                                  this.currentTask = "Discovering table schema structures...";
                              }
                          } else if (data.type === 'tool_output') {
                              if (this.debugMode) {
                                  this.logActivity(`TOOL OUTPUT: ${data.content}`);
                              }
                          } else if (data.type === 'a2ui') {
                              this.processor.processMessages(data.content);
                          } else if (data.type === 'text') {
                              this.startTalkingAnimation();
                              fullMarkdown += data.content;
                              parser.append(data.content);
                              
                              const newMessages = [...this.messages];
                              newMessages[currentAgentMessageIndex] = { 
                                  role: 'agent', 
                                  content: fullMarkdown
                              };
                              this.messages = newMessages;
                          }
                      } catch (e) {
                          console.error("Error parsing JSON line:", line, e);
                      }
                  }
              }
          }

      } catch (e) {
          clearInterval(this.thinkBlinkInterval);
          this.currentTask = null;
          this.avatarState = 'error';
          this.avatarLabelText = "STATUS: ERROR";
          this.avatarLabelColor = "var(--pc98-red)";
          this.dialogueText = "ERROR: Connection with the diagnostic server was interrupted.";
          this.logActivity("ERROR: CONNECTION LOST!", false, "error");
          
          let currentAgentMessageIndex = this.messages.length - 1;
          const newMessages = [...this.messages];
          newMessages[currentAgentMessageIndex] = { 
              role: 'agent', 
              content: "ERROR: CONNECTION LOST" 
          };
          this.messages = newMessages;
      }
  }

  private handleSubmit(e: Event) {
      e.preventDefault();
      this.sendMessage(this.inputEl.value);
  }

  private closeSurface(surfaceId: string) {
      const next = new Map(this.activeSurfaces);
      next.delete(surfaceId);
      this.activeSurfaces = next;
      this.logActivity(`DISMISSED SURFACE '${surfaceId}'.`);
  }

  private hasVisibleComponents(surface: any): boolean {
      if (!surface || !surface.componentsModel) return false;
      try {
          const entries = Array.from(surface.componentsModel.entries);
          for (const entry of entries) {
              if (Array.isArray(entry) && entry[1]) {
                  const comp = entry[1] as any;
                  if (comp.type !== 'AidaDialogueBox' && comp.type !== 'Column' && comp.type !== 'Row') {
                      return true;
                  }
              }
          }
      } catch (e) {
          console.error("Error checking visible components", e);
      }
      return false;
  }



  render() {
    return html`
      <div id="main-container" class="a2ui-dark">
          <div id="canvas-container">
              <div class="canvas-title">*** EMERGENCY DIAGNOSTIC AGENT ***</div>
              
              <!-- Permanent JRPG-style dialogue box at the top of the workspace canvas -->
              <div class="canvas-surface-container" style="margin-bottom: 20px; flex-shrink: 0;">
                  <div class="canvas-surface-header">
                      <span>SYSTEM DIALOGUE CONSOLE</span>
                  </div>
                  <div class="canvas-surface-body" style="display: flex; gap: 20px; align-items: flex-start; background-color: #000011; padding: 15px;">
                      <div id="boot-avatar-pane" style="flex-shrink: 0; width: 256px;">
                          <div id="avatar-window" style="width: 256px; height: 256px; border: 3px ridge var(--pc98-border);">
                              <img src="/${this.avatarState}?cb=${this.cacheBuster}" alt="Agent Avatar" id="avatar-img">
                          </div>
                          <div id="avatar-label" style="color: ${this.avatarLabelColor};">
                              <span class="glowing-dot ${this.avatarState === 'error' ? 'error' : this.avatarState.startsWith('think') ? 'thinking' : ''}"></span>
                              ${this.avatarLabelText}
                          </div>
                      </div>
                      <div style="display: flex; flex-direction: column; flex: 1; gap: 15px;">
                          <div id="jrpg-bubble" style="border: 3px ridge var(--pc98-border); padding: 15px; background: #000000;">
                              <div class="character-name" style="color: var(--pc98-green); font-size: 20px; font-weight: bold; margin-bottom: 5px; border-bottom: 1px solid var(--pc98-border); padding-bottom: 3px;">AIDA</div>
                              <div class="bubble-text">${this.dialogueText}</div>
                          </div>
                          ${this.currentTask ? html`
                              <div style="border: 2px solid var(--pc98-cyan); padding: 10px 15px; background-color: #000022; color: var(--pc98-cyan); font-family: inherit; font-size: 20px; display: flex; align-items: center; gap: 10px; flex-shrink: 0; line-height: 1.2;">
                                  <span style="color: var(--pc98-amber); font-weight: bold; animation: blink 1.2s infinite;">[ACTIVE TASK]</span>
                                  <span>${this.currentTask}</span>
                              </div>
                          ` : ''}
                      </div>
                  </div>
              </div>

              <div id="canvas-viewport">
                  <!-- Dynamic A2UI Surfaces Rendered Here -->
                  ${Array.from(this.activeSurfaces.values())
                     .filter(surface => this.hasVisibleComponents(surface))
                     .map(surface => html`
                     <div class="canvas-surface-container">
                        <div class="canvas-surface-header">
                           <span class="surface-title">SURFACE: ${surface.id.toUpperCase()}</span>
                           <button class="close-btn" @click=${() => this.closeSurface(surface.id)}>[X] CLOSE</button>
                        </div>
                        <div class="canvas-surface-body">
                           <a2ui-surface .surface=${surface}></a2ui-surface>
                        </div>
                     </div>
                  `)}
              </div>

              <form id="user-input" @submit=${this.handleSubmit}>
                  <span id="prompt-symbol">AIDA&gt;</span>
                  <input type="text" id="message-text" autocomplete="off" autofocus placeholder="State your emergency... (e.g., 'check cpu usage', 'show logs', 'find large tables')" />
              </form>
          </div>
      </div>
    `;
  }
}
