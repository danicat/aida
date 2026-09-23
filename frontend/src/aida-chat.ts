import { LitElement, html, css, nothing } from 'lit';
import { customElement, state, query } from 'lit/decorators.js';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { MessageProcessor } from '@a2ui/web_core/v0_9';
import { basicCatalog, Context } from '@a2ui/lit/v0_9';
import { aidaCustomCatalog } from './aida-catalog/index.js';
import { provide } from '@lit/context';
import { renderMarkdown } from '@a2ui/markdown-it';
import MarkdownIt from 'markdown-it';
import '@a2ui/lit/v0_9'; // Registers the <a2ui-surface> component
import { streamAgentResponse } from './protocol.js';

const mdRenderer = new MarkdownIt({ html: false, linkify: true, breaks: true });

export interface SystemStatus {
  os: string;
  hostname: string;
  kernel: string;
  uptime: string;
  health: 'NOMINAL' | 'WARNING' | 'CRITICAL';
  cpu?: number;
  memory?: number;
}

export interface ChatTurn {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  status?: string;
  surfaceIds: string[];
}

@customElement('aida-chat')
export class AidaChat extends LitElement {
  @provide({ context: Context.markdown })
  markdownRenderer = renderMarkdown;

  // --- Reactive States ---
  @state() private turns: ChatTurn[] = [];
  @state() private activeSurfaces: Map<string, any> = new Map();
  @state() private avatarState: 'idle' | 'blink' | 'talk' | 'think' | 'think_blink' | 'error' = 'idle';
  @state() private avatarLabelText = 'ONLINE';
  @state() private avatarLabelColor = 'var(--pc98-green)';
  @state() private statusBarText = 'IDLE - AWAITING INPUT';
  @state() private isStreaming = false;
  @state() private showLogs = false;
  @state() private logs: Array<{ time: string; content: string; type: 'normal' | 'error' }> = [];
  @state() private cacheBuster = Date.now();
  @state() private systemStatus: SystemStatus = {
    hostname: 'AIDA-DIAG-NODE',
    os: 'Darwin (macOS)',
    kernel: 'Darwin Kernel 25.3.0',
    uptime: '14h 22m',
    health: 'NOMINAL'
  };

  @query('#message-text') private inputEl!: HTMLInputElement;
  @query('#canvas-viewport') private canvasViewport!: HTMLElement;
  @query('#log-window') private logWindow!: HTMLElement;

  private processor!: MessageProcessor<any>;
  private animationInterval: any = null;
  private thinkBlinkInterval: any = null;
  private statusPollTimer: any = null;
  private activeAgentTurnId: string | null = null;
  private abortController: AbortController | null = null;

  static styles = css`
    :host {
      display: block;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      background-color: var(--pc98-bg, #000022);
      color: var(--pc98-fg, #d4d4d4);
      font-family: 'VT323', monospace;
      font-size: var(--aida-font-size-base, 24px);
      box-sizing: border-box;
    }

    * {
      box-sizing: border-box;
    }

    #app-container {
      display: flex;
      flex-direction: column;
      width: 100%;
      height: 100%;
      max-width: 1440px;
      margin: 0 auto;
      border-left: 3px double var(--pc98-border, #5555aa);
      border-right: 3px double var(--pc98-border, #5555aa);
      background-color: var(--pc98-bg, #000022);
      position: relative;
      overflow: hidden;
    }

    /* =========================================================================
       FIXED HEADER (TOP)
       ========================================================================= */
    #fixed-header {
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 28px;
      padding: 16px 28px;
      background-color: var(--pc98-dark-gray, #222244);
      border-bottom: 4px double var(--pc98-border, #5555aa);
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
      z-index: 100;
      min-height: 380px;
      font-size: calc(var(--aida-font-size-base) + 5.33px); /* Increased default font size of header by 4pt (~5.33px) */
    }

    /* Left Pane: Host Info & Status Readout below it */
    .header-left-pane {
      display: flex;
      flex-direction: column;
      flex: 1;
      gap: 16px;
      min-width: 0;
    }

    .header-sysinfo {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .sysinfo-title-row {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }

    .sys-badge {
      color: var(--pc98-amber, #ffb700);
      font-size: 1em;
      font-weight: bold;
    }

    .sys-title {
      color: var(--pc98-green, #55ff55);
      font-size: 1.2em;
      font-weight: bold;
      text-shadow: 0 0 6px var(--pc98-green, #55ff55);
      letter-spacing: 0.5px;
    }

    .sysinfo-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      column-gap: 24px;
      row-gap: 6px;
      font-size: 0.88em;
      line-height: 1.35;
    }

    .spec-item .k {
      color: var(--pc98-cyan, #00ffff);
      margin-right: 6px;
    }

    .spec-item .v {
      color: var(--pc98-fg, #d4d4d4);
    }

    .health-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 3px 10px;
      border: 1px solid var(--pc98-border, #5555aa);
      background-color: #000000;
      font-weight: bold;
      letter-spacing: 0.5px;
      font-size: 0.88em;
    }

    .health-badge.nominal {
      color: var(--pc98-green, #55ff55);
      border-color: var(--pc98-green, #55ff55);
    }

    .health-badge.warning {
      color: var(--pc98-amber, #ffb700);
      border-color: var(--pc98-amber, #ffb700);
    }

    .health-badge.critical {
      color: var(--pc98-red, #ff5555);
      border-color: var(--pc98-red, #ff5555);
    }

    /* Operational Status Readout - Placed below System Info (Multi-line 3 lines) */
    .header-status-panel {
      display: flex;
      flex-direction: column;
      gap: 6px;
      width: 100%;
    }

    .status-panel-label {
      font-size: 0.82em;
      color: var(--pc98-cyan, #00ffff);
      text-shadow: 0 0 4px var(--pc98-cyan, #00ffff);
      letter-spacing: 1px;
    }

    .status-lcd-bezel {
      position: relative;
      background-color: #000010;
      border: 2px inset var(--pc98-border, #5555aa);
      padding: 10px 16px;
      height: calc(1.4em * 3 + 20px);
      min-height: calc(1.4em * 3 + 20px);
      max-height: calc(1.4em * 3 + 20px);
      display: flex;
      align-items: flex-start;
      overflow: hidden;
      box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.9);
    }

    .status-lcd-scanline {
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: repeating-linear-gradient(0deg, rgba(0,0,0,0.35) 0px, rgba(0,0,0,0.35) 1px, transparent 1px, transparent 2px);
      pointer-events: none;
    }

    .status-lcd-text {
      color: var(--pc98-green, #55ff55);
      text-shadow: 0 0 8px var(--pc98-green, #55ff55);
      font-size: 1.05em;
      line-height: 1.4;
      letter-spacing: 0.5px;
      white-space: pre-wrap;
      word-break: break-word;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      z-index: 1;
      width: 100%;
      animation: textPulse 2s infinite alternate ease-in-out;
    }

    @keyframes textPulse {
      from { opacity: 0.9; }
      to { opacity: 1; text-shadow: 0 0 12px var(--pc98-green, #55ff55); }
    }

    /* Right: AIDA Avatar Column - 2x Size */
    .header-avatar-col {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .avatar-name {
      color: var(--pc98-green, #55ff55);
      font-size: 1.15em;
      font-weight: bold;
      text-shadow: 0 0 6px var(--pc98-green, #55ff55);
      letter-spacing: 1.5px;
      text-align: center;
    }

    .avatar-frame {
      width: 280px;
      height: 280px;
      min-width: 280px;
      min-height: 280px;
      border: 4px ridge var(--pc98-border, #5555aa);
      background-color: #000000;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      image-rendering: pixelated;
      box-shadow: 0 0 16px rgba(85, 85, 170, 0.7);
    }

    .avatar-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      image-rendering: pixelated;
    }

    .avatar-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 4px 14px;
      border: 1px solid var(--pc98-border, #5555aa);
      background-color: #000000;
      font-size: 0.88em;
      font-weight: bold;
      text-align: center;
      min-width: 180px;
    }

    .header-btns {
      display: flex;
      justify-content: center;
      gap: 10px;
      width: 100%;
    }

    .hdr-btn {
      padding: 4px 14px;
      background-color: var(--pc98-bg, #000022);
      color: var(--pc98-cyan, #00ffff);
      border: 1px solid var(--pc98-border, #5555aa);
      font-family: 'VT323', monospace;
      font-size: 0.88em;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .hdr-btn:hover {
      background-color: var(--pc98-cyan, #00ffff);
      color: #000000;
    }

    .hdr-btn.active {
      background-color: var(--pc98-green, #55ff55);
      color: #000000;
      border-color: var(--pc98-green, #55ff55);
    }

    /* Glowing Pulse Dot */
    .pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
    }

    .pulse-dot.nominal {
      background-color: var(--pc98-green, #55ff55);
      box-shadow: 0 0 6px var(--pc98-green, #55ff55);
      animation: pulseGreen 1.5s infinite;
    }

    .pulse-dot.warning, .pulse-dot.thinking {
      background-color: var(--pc98-amber, #ffb700);
      box-shadow: 0 0 6px var(--pc98-amber, #ffb700);
      animation: pulseAmber 1s infinite;
    }

    .pulse-dot.critical, .pulse-dot.error {
      background-color: var(--pc98-red, #ff5555);
      box-shadow: 0 0 6px var(--pc98-red, #ff5555);
      animation: pulseRed 0.8s infinite;
    }

    @keyframes pulseGreen {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }

    @keyframes pulseAmber {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.3; transform: scale(0.8); }
    }

    @keyframes pulseRed {
      0%, 100% { opacity: 1; transform: scale(1.1); }
      50% { opacity: 0.3; transform: scale(0.75); }
    }

    /* =========================================================================
       FREE CANVAS / CONVERSATION STREAM (BOTTOM)
       ========================================================================= */
    #canvas-viewport {
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      background-color: var(--pc98-bg, #000022);
      scrollbar-width: thin;
      scrollbar-color: var(--pc98-border, #5555aa) #000011;
    }

    #canvas-viewport::-webkit-scrollbar {
      width: 8px;
    }
    #canvas-viewport::-webkit-scrollbar-track {
      background: #000011;
    }
    #canvas-viewport::-webkit-scrollbar-thumb {
      background: var(--pc98-border, #5555aa);
    }

    /* Empty State Landing */
    .empty-state {
      margin: auto;
      text-align: center;
      max-width: 650px;
      border: 3px double var(--pc98-border, #5555aa);
      background-color: var(--pc98-dark-gray, #222244);
      padding: 30px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.7);
    }

    .empty-banner {
      color: var(--pc98-green, #55ff55);
      font-size: calc(var(--aida-font-size-base) * 1.2);
      font-weight: bold;
      text-shadow: 0 0 8px var(--pc98-green, #55ff55);
      margin-bottom: 12px;
    }

    .empty-hint {
      color: var(--pc98-fg, #d4d4d4);
      font-size: calc(var(--aida-font-size-base) * 0.9);
      margin-bottom: 20px;
    }

    .quick-prompts {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .quick-btn {
      padding: 10px;
      background-color: #000000;
      color: var(--pc98-cyan, #00ffff);
      border: 2px solid var(--pc98-border, #5555aa);
      font-family: 'VT323', monospace;
      font-size: calc(var(--aida-font-size-base) * 0.85);
      cursor: pointer;
      text-align: left;
      transition: all 0.15s ease;
    }

    .quick-btn:hover {
      background-color: var(--pc98-cyan, #00ffff);
      color: #000000;
      border-color: #ffffff;
    }

    /* Turn Entries */
    .turn-card {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 14px 18px;
      border: 2px solid var(--pc98-border, #5555aa);
      background-color: #000016;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
    }

    .turn-card.user-turn {
      border-color: var(--pc98-cyan, #00ffff);
      background-color: rgba(0, 255, 255, 0.03);
    }

    .turn-card.agent-turn {
      border-color: var(--pc98-border, #5555aa);
      background-color: var(--pc98-dark-gray, #222244);
    }

    .turn-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(85, 85, 170, 0.4);
      padding-bottom: 6px;
      font-size: calc(var(--aida-font-size-base) * 0.8);
    }

    .turn-prefix {
      font-weight: bold;
    }

    .user-turn .turn-prefix {
      color: var(--pc98-cyan, #00ffff);
      text-shadow: 0 0 4px var(--pc98-cyan, #00ffff);
    }

    .agent-turn .turn-prefix {
      color: var(--pc98-green, #55ff55);
      text-shadow: 0 0 4px var(--pc98-green, #55ff55);
    }

    .turn-time {
      color: var(--pc98-border, #5555aa);
      font-size: calc(var(--aida-font-size-base) * 0.7);
    }

    .turn-body {
      font-size: var(--aida-font-size-base);
      line-height: 1.35;
      word-break: break-word;
    }

    .turn-body.user-body {
      color: var(--pc98-cyan, #00ffff);
      font-size: calc(var(--aida-font-size-base) * 1.05);
    }

    .turn-body.agent-body {
      color: var(--pc98-fg, #d4d4d4);
    }

    /* Markdown styling inside Agent Turns */
    .agent-body p {
      margin: 4px 0 8px 0;
    }

    .agent-body code {
      font-family: 'VT323', monospace;
      font-size: inherit;
      background-color: #000000;
      color: var(--pc98-cyan, #00ffff);
      padding: 2px 6px;
      border: 1px solid var(--pc98-border, #5555aa);
    }

    .agent-body pre {
      font-family: 'VT323', monospace;
      font-size: inherit;
      background-color: #000000;
      color: var(--pc98-green, #55ff55);
      padding: 12px;
      border: 2px solid var(--pc98-border, #5555aa);
      overflow-x: auto;
      margin: 8px 0;
      white-space: pre-wrap;
    }

    .agent-body pre code {
      background: none;
      padding: 0;
      border: none;
      color: inherit;
    }

    .agent-body strong, .agent-body b {
      color: var(--pc98-green, #55ff55);
      font-weight: bold;
    }

    .agent-body ul, .agent-body ol {
      margin: 4px 0 8px 20px;
      padding: 0;
    }

    /* Inline A2UI Surfaces Container */
    .turn-inline-surfaces {
      display: flex;
      flex-direction: column;
      gap: 14px;
      margin-top: 12px;
    }

    .inline-surface-card {
      border: 3px ridge var(--pc98-border, #5555aa);
      background-color: #000000;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
    }

    .inline-surface-hdr {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 12px;
      background-color: var(--pc98-dark-gray, #222244);
      border-bottom: 2px solid var(--pc98-border, #5555aa);
    }

    .inline-surface-title {
      color: var(--pc98-green, #55ff55);
      font-size: calc(var(--aida-font-size-base) * 0.8);
      font-weight: bold;
      letter-spacing: 0.5px;
    }

    .surface-close-btn {
      padding: 2px 8px;
      background-color: var(--pc98-bg, #000022);
      color: var(--pc98-red, #ff5555);
      border: 1px solid var(--pc98-red, #ff5555);
      font-family: 'VT323', monospace;
      font-size: calc(var(--aida-font-size-base) * 0.75);
      cursor: pointer;
    }

    .surface-close-btn:hover {
      background-color: var(--pc98-red, #ff5555);
      color: #000000;
    }

    .inline-surface-body {
      padding: 12px;
      background-color: #000000;
      overflow-x: auto;
    }

    /* =========================================================================
       DIAGNOSTIC LOG DRAWER (COLLAPSIBLE)
       ========================================================================= */
    #diagnostic-drawer {
      flex-shrink: 0;
      height: 160px;
      display: flex;
      flex-direction: column;
      background-color: #000010;
      border-top: 3px ridge var(--pc98-border, #5555aa);
      border-bottom: 2px solid var(--pc98-border, #5555aa);
    }

    .drawer-hdr {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4px 12px;
      background-color: var(--pc98-dark-gray, #222244);
      color: var(--pc98-cyan, #00ffff);
      font-size: calc(var(--aida-font-size-base) * 0.75);
      font-weight: bold;
    }

    .drawer-body {
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      padding: 8px 12px;
      font-size: calc(var(--aida-font-size-base) * 0.75);
      line-height: 1.25;
      color: var(--pc98-green, #55ff55);
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .log-entry.error {
      color: var(--pc98-red, #ff5555);
    }

    .log-time {
      color: var(--pc98-border, #5555aa);
      margin-right: 8px;
    }

    /* =========================================================================
       PROMPT INPUT BAR (BOTTOM PINNED)
       ========================================================================= */
    #input-footer {
      flex-shrink: 0;
      border-top: 4px double var(--pc98-border, #5555aa);
      background-color: var(--pc98-dark-gray, #222244);
      padding: 12px 18px;
      box-shadow: 0 -4px 15px rgba(0, 0, 0, 0.6);
      z-index: 100;
    }

    #user-input {
      display: flex;
      align-items: center;
      gap: 12px;
      width: 100%;
    }

    #prompt-symbol {
      color: var(--pc98-green, #55ff55);
      font-size: calc(var(--aida-font-size-base) * 1.15);
      font-weight: bold;
      text-shadow: 0 0 6px var(--pc98-green, #55ff55);
      flex-shrink: 0;
    }

    #message-text {
      flex: 1;
      background-color: #000000;
      border: 2px solid var(--pc98-border, #5555aa);
      color: var(--pc98-green, #55ff55);
      font-family: 'VT323', monospace;
      font-size: var(--aida-font-size-base);
      padding: 8px 12px;
      outline: none;
      min-width: 0;
      box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.8);
    }

    #message-text:focus {
      border-color: var(--pc98-cyan, #00ffff);
      box-shadow: 0 0 8px rgba(0, 255, 255, 0.4);
    }

    #message-text::placeholder {
      color: var(--pc98-border, #5555aa);
    }

    #submit-btn {
      padding: 8px 18px;
      background-color: var(--pc98-bg, #000022);
      color: var(--pc98-green, #55ff55);
      border: 2px solid var(--pc98-green, #55ff55);
      font-family: 'VT323', monospace;
      font-size: calc(var(--aida-font-size-base) * 0.9);
      font-weight: bold;
      cursor: pointer;
      flex-shrink: 0;
      transition: all 0.15s ease;
    }

    #submit-btn:hover:not(:disabled) {
      background-color: var(--pc98-green, #55ff55);
      color: #000000;
    }

    #submit-btn:disabled, #message-text:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    @media (max-width: 900px) {
      #fixed-header {
        flex-wrap: wrap;
        gap: 12px;
        padding: 10px 14px;
        min-height: auto;
      }
      .avatar-frame {
        width: 120px;
        height: 120px;
        min-width: 120px;
        min-height: 120px;
      }
      .header-sysinfo {
        min-width: 100%;
        order: 2;
      }
      .header-status-panel {
        max-width: 100%;
        order: 3;
      }
      .header-avatar-col {
        order: 1;
        width: 100%;
        justify-content: center;
      }
    }
  `;

  constructor() {
    super();
    this.initProcessor();
  }

  connectedCallback() {
    super.connectedCallback();
    this.startBlinking();
    this.fetchSystemStatus();
    this.logActivity('AIDA RETRO SYSTEM ONLINE. AWAITING DIAGNOSTIC TELEMETRY.');

    // Status polling every 15 seconds
    this.statusPollTimer = setInterval(() => {
      this.fetchSystemStatus();
    }, 15000);

    // Initial greeting turn if no turns yet
    if (this.turns.length === 0) {
      this.turns = [
        {
          id: 'turn-init',
          role: 'agent',
          content: 'EMERGENCY DIAGNOSTIC AGENT READY. State your system emergency or query to begin telemetry analysis.',
          timestamp: this.formatTime(),
          surfaceIds: []
        }
      ];
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.stopTalkingAnimation();
    this.stopBlinking();
    if (this.statusPollTimer) {
      clearInterval(this.statusPollTimer);
      this.statusPollTimer = null;
    }
  }

  private initProcessor() {
    this.processor = new MessageProcessor([basicCatalog, aidaCustomCatalog], (action: any) => {
      console.log('A2UI ACTION TRIGGERED:', action);

      let actionName = 'submit';
      let resolvedContext: any = {};

      if (typeof action === 'string') {
        actionName = action;
      } else if (action && typeof action === 'object') {
        const payload = action.action || action;
        actionName = payload.name || (payload.event && payload.event.name) || 'submit';
        const contextObj = payload.context || (payload.event && payload.event.context) || payload;

        if (Array.isArray(contextObj)) {
          contextObj.forEach((ctx: any) => {
            if (ctx && typeof ctx === 'object' && 'key' in ctx && 'value' in ctx) {
              resolvedContext[ctx.key] = ctx.value;
            }
          });
        } else if (contextObj && typeof contextObj === 'object') {
          Object.keys(contextObj).forEach(key => {
            if (['name', 'event', 'surfaceId', 'sourceComponentId', 'timestamp', 'version', 'action'].includes(key)) {
              return;
            }
            resolvedContext[key] = contextObj[key];
          });
        }
      }

      let responseText = actionName;
      if (Object.keys(resolvedContext).length > 0) {
        responseText = `Action: ${actionName}\nContext:\n` +
          Object.keys(resolvedContext).map(k => `- ${k}: ${JSON.stringify(resolvedContext[k])}`).join('\n');
      }

      this.logActivity(`INTERACTION SUBMITTED: ${actionName}`);
      this.sendMessage(responseText, false);
    });

    this.processor.onSurfaceCreated((surface: any) => {
      this.activeSurfaces = new Map(this.activeSurfaces.set(surface.id, surface));

      // Associate with current active agent turn
      if (this.activeAgentTurnId) {
        const turnIndex = this.turns.findIndex(t => t.id === this.activeAgentTurnId);
        if (turnIndex !== -1) {
          const turn = this.turns[turnIndex];
          if (!turn.surfaceIds.includes(surface.id)) {
            const updatedTurns = [...this.turns];
            updatedTurns[turnIndex] = {
              ...turn,
              surfaceIds: [...turn.surfaceIds, surface.id]
            };
            this.turns = updatedTurns;
          }
        }
      }

      // Re-render when components change
      surface.componentsModel.onCreated.subscribe((comp: any) => {
        this.activeSurfaces = new Map(this.activeSurfaces);
        this.requestUpdate();
        if (comp && comp.onUpdated) {
          comp.onUpdated.subscribe(() => {
            this.activeSurfaces = new Map(this.activeSurfaces);
            this.requestUpdate();
          });
        }
      });
      surface.componentsModel.onDeleted.subscribe(() => {
        this.activeSurfaces = new Map(this.activeSurfaces);
        this.requestUpdate();
      });
    });

    this.processor.onSurfaceDeleted((surfaceId: string) => {
      const next = new Map(this.activeSurfaces);
      next.delete(surfaceId);
      this.activeSurfaces = next;
      this.requestUpdate();
    });
  }

  // --- System Status Polling ---
  private async fetchSystemStatus() {
    try {
      const res = await fetch('/api/system-status');
      if (res.ok) {
        const data = await res.json();
        this.systemStatus = {
          hostname: data.hostname || this.systemStatus.hostname,
          os: data.os || this.systemStatus.os,
          kernel: data.kernel || this.systemStatus.kernel,
          uptime: data.uptime || this.systemStatus.uptime,
          health: (data.health || 'NOMINAL').toUpperCase() as any,
          cpu: data.cpu,
          memory: data.memory
        };
      }
    } catch {
      // Retain fallback defaults smoothly
    }
  }

  // --- Avatar Animation & States ---
  private startBlinking() {
    this.stopBlinking();
    const scheduleNextBlink = () => {
      const delay = 2500 + Math.random() * 3500;
      this.thinkBlinkInterval = setTimeout(() => {
        if (this.avatarState === 'idle') {
          this.avatarState = 'blink';
          this.cacheBuster = Date.now();
          setTimeout(() => {
            if (this.avatarState === 'blink') {
              this.avatarState = 'idle';
              this.cacheBuster = Date.now();
            }
            scheduleNextBlink();
          }, 150);
        } else {
          scheduleNextBlink();
        }
      }, delay);
    };
    scheduleNextBlink();
  }

  private stopBlinking() {
    if (this.thinkBlinkInterval) {
      clearTimeout(this.thinkBlinkInterval);
      this.thinkBlinkInterval = null;
    }
  }

  private startTalkingAnimation() {
    if (this.animationInterval) return;
    this.stopBlinking();
    let toggle = false;
    this.avatarState = 'talk';
    this.avatarLabelText = 'RESPONDING';
    this.avatarLabelColor = 'var(--pc98-green)';
    this.cacheBuster = Date.now();

    this.animationInterval = setInterval(() => {
      toggle = !toggle;
      this.avatarState = toggle ? 'talk' : 'idle';
      this.cacheBuster = Date.now();
    }, 150);
  }

  private stopTalkingAnimation() {
    if (this.animationInterval) {
      clearInterval(this.animationInterval);
      this.animationInterval = null;
    }
  }

  private setIdleState() {
    this.stopTalkingAnimation();
    this.avatarState = 'idle';
    this.avatarLabelText = 'ONLINE';
    this.avatarLabelColor = 'var(--pc98-green)';
    this.statusBarText = 'IDLE - AWAITING INPUT';
    this.isStreaming = false;
    this.cacheBuster = Date.now();
    this.startBlinking();
  }

  private setThinkingState() {
    this.stopTalkingAnimation();
    this.stopBlinking();
    this.avatarState = 'think';
    this.avatarLabelText = 'THINKING';
    this.avatarLabelColor = 'var(--pc98-amber)';
    this.statusBarText = 'THINKING...';
    this.cacheBuster = Date.now();
  }

  private setErrorState(message: string) {
    this.stopTalkingAnimation();
    this.stopBlinking();
    this.avatarState = 'error';
    this.avatarLabelText = 'ERROR';
    this.avatarLabelColor = 'var(--pc98-red)';
    this.statusBarText = 'ERROR - TRANSMISSION INTERRUPTED';
    this.isStreaming = false;
    this.cacheBuster = Date.now();
    this.logActivity(`ERROR: ${message}`, 'error');
  }

  private formatTime(): string {
    const d = new Date();
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;
  }

  private logActivity(content: string, type: 'normal' | 'error' = 'normal') {
    this.logs = [...this.logs, { time: `[${this.formatTime()}]`, content, type }];
    setTimeout(() => {
      if (this.logWindow) {
        this.logWindow.scrollTop = this.logWindow.scrollHeight;
      }
    }, 50);
  }

  private scrollCanvasToBottom() {
    setTimeout(() => {
      if (this.canvasViewport) {
        this.canvasViewport.scrollTop = this.canvasViewport.scrollHeight;
      }
    }, 50);
  }

  // --- User Message Transmission ---
  private async sendMessage(text: string, showInUi = true) {
    const trimmed = text.trim();
    if (!trimmed || this.isStreaming) return;

    if (this.inputEl && showInUi) {
      this.inputEl.value = '';
    }

    // Add user turn if requested
    if (showInUi) {
      const userTurn: ChatTurn = {
        id: `turn-${Date.now()}-user`,
        role: 'user',
        content: trimmed,
        timestamp: this.formatTime(),
        surfaceIds: []
      };
      this.turns = [...this.turns, userTurn];
      this.scrollCanvasToBottom();
    }

    // Create a new agent turn to hold streaming response & surfaces
    const agentTurnId = `turn-${Date.now()}-agent`;
    this.activeAgentTurnId = agentTurnId;
    const agentTurn: ChatTurn = {
      id: agentTurnId,
      role: 'agent',
      content: '',
      timestamp: this.formatTime(),
      status: 'RECEIVING TRANSMISSION...',
      surfaceIds: []
    };
    this.turns = [...this.turns, agentTurn];
    this.scrollCanvasToBottom();

    this.isStreaming = true;
    this.setThinkingState();

    this.abortController = new AbortController();

    // Invoke clean typed protocol handler (ZERO REGEX!)
    await streamAgentResponse(
      trimmed,
      {
        onTextDelta: (delta: string) => {
          this.startTalkingAnimation();
          const turnIdx = this.turns.findIndex(t => t.id === agentTurnId);
          if (turnIdx !== -1) {
            const current = this.turns[turnIdx];
            const updated = [...this.turns];
            updated[turnIdx] = {
              ...current,
              content: current.content + delta,
              status: undefined
            };
            this.turns = updated;
            this.scrollCanvasToBottom();
          }
        },
        onToolStart: (toolName: string) => {
          this.setThinkingState();
          this.logActivity(`EXECUTING TOOL: ${toolName}`);
          if (toolName.includes('osquery')) {
            this.statusBarText = 'EXECUTING QUERY: SELECT...';
          } else if (toolName.includes('skill')) {
            this.statusBarText = 'LOADING SKILL...';
          } else {
            this.statusBarText = `EXECUTING: ${toolName.toUpperCase()}...`;
          }
        },
        onToolResult: () => {
          this.setThinkingState();
        },
        onA2uiOperations: (ops: any[]) => {
          try {
            // Pre-process ops: if any surface already exists, delete it first to avoid duplicate surface errors
            for (const op of ops) {
              const sId = op.createSurface?.surfaceId;
              if (sId && this.processor.model.getSurface(sId)) {
                try {
                  this.processor.processMessages([{ version: 'v0.9', deleteSurface: { surfaceId: sId } }]);
                } catch (e) {
                  console.warn('Could not reset existing surface:', e);
                }
              }
              if (op.createSurface && !op.createSurface.catalogId) {
                op.createSurface.catalogId = 'aida_custom';
              }
            }

            this.processor.processMessages(ops);

            // Associate referenced surfaceIds with current agent turn
            if (this.activeAgentTurnId) {
              const turnIndex = this.turns.findIndex(t => t.id === this.activeAgentTurnId);
              if (turnIndex !== -1) {
                const turn = this.turns[turnIndex];
                const updatedSurfaceIds = new Set(turn.surfaceIds || []);
                for (const op of ops) {
                  const sId = op.createSurface?.surfaceId || op.updateComponents?.surfaceId || op.updateDataModel?.surfaceId;
                  if (sId) updatedSurfaceIds.add(sId);
                }
                const updatedTurns = [...this.turns];
                updatedTurns[turnIndex] = {
                  ...turn,
                  surfaceIds: Array.from(updatedSurfaceIds)
                };
                this.turns = updatedTurns;
              }
            }

            // Sync surfaces into activeSurfaces Map
            for (const op of ops) {
              const sId = op.createSurface?.surfaceId || op.updateComponents?.surfaceId;
              if (sId) {
                const surface = this.processor.model.getSurface(sId);
                if (surface) {
                  this.activeSurfaces.set(sId, surface);
                }
              }
            }

            this.activeSurfaces = new Map(this.activeSurfaces);
            this.requestUpdate();
            this.logActivity(`A2UI OPERATIONS APPLIED (${ops.length} ops)`);
          } catch (e: any) {
            console.error('Failed to process A2UI operations:', e);
            this.logActivity(`A2UI ERROR: ${e?.message || e}`, 'error');
          }
        },
        onStatusChange: (statusText: string) => {
          this.statusBarText = statusText;
        },
        onRunStarted: () => {
          this.setThinkingState();
        },
        onRunFinished: () => {
          this.setIdleState();
          this.scrollCanvasToBottom();
        },
        onError: (err: string) => {
          this.setErrorState(err);
          const turnIdx = this.turns.findIndex(t => t.id === agentTurnId);
          if (turnIdx !== -1) {
            const current = this.turns[turnIdx];
            const updated = [...this.turns];
            updated[turnIdx] = {
              ...current,
              content: current.content ? `${current.content}\n\n[TRANSMISSION FAILED: ${err}]` : `[TRANSMISSION FAILED: ${err}]`,
              status: 'ERROR'
            };
            this.turns = updated;
          }
        },
        onLog: (logMsg: string) => {
          this.logActivity(logMsg);
        }
      },
      this.abortController.signal
    );
  }

  private handleSubmit(e: Event) {
    e.preventDefault();
    this.sendMessage(this.inputEl.value);
  }

  private toggleLogs() {
    this.showLogs = !this.showLogs;
  }

  private async clearSession() {
    try {
      await fetch('/session/clear', { method: 'POST' });
    } catch {
      // ignore
    }
    this.turns = [
      {
        id: `turn-${Date.now()}-reset`,
        role: 'system',
        content: '[SYSTEM MEMORY CLEARED. DIAGNOSTIC BUFFER RESET.]',
        timestamp: this.formatTime(),
        surfaceIds: []
      }
    ];
    this.activeSurfaces.clear();
    this.logActivity('SESSION MEMORY RESET BY OPERATOR.');
    this.setIdleState();
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
      return entries.length > 0;
    } catch {
      return true;
    }
  }

  // --- Render Helpers ---
  private cleanA2uiText(text: string): string {
    if (!text) return '';
    let cleaned = text.replace(/<a2ui[\s\S]*?<\/a2ui>/gi, '');
    cleaned = cleaned.replace(/<a2ui[\s\S]*$/gi, '');
    return cleaned.trim();
  }

  private renderAgentMarkdown(content: string) {
    try {
      const clean = this.cleanA2uiText(content);
      if (!clean) return nothing;
      const htmlStr = mdRenderer.render(clean);
      return unsafeHTML(htmlStr);
    } catch {
      const clean = this.cleanA2uiText(content);
      return clean ? html`<div>${clean}</div>` : nothing;
    }
  }

  private renderTurn(turn: ChatTurn) {
    return html`
      <div class="turn-card ${turn.role}-turn">
        <div class="turn-header">
          <span class="turn-prefix">${turn.role === 'user' ? 'USER>' : turn.role === 'system' ? 'SYSTEM>' : 'AIDA>'}</span>
          <span class="turn-time">${turn.timestamp}</span>
        </div>

        ${turn.role === 'user'
          ? html`<div class="turn-body user-body">${turn.content}</div>`
          : html`
              <div class="turn-body agent-body">
                ${turn.content ? this.renderAgentMarkdown(turn.content) : nothing}
                ${this.renderInlineSurfaces(turn)}
              </div>
            `}
      </div>
    `;
  }

  private renderInlineSurfaces(turn: ChatTurn) {
    if (!turn.surfaceIds || turn.surfaceIds.length === 0) return nothing;

    const surfacesToRender = turn.surfaceIds
      .map(id => this.activeSurfaces.get(id) || this.processor?.model?.getSurface(id))
      .filter((s): s is any => !!s && this.hasVisibleComponents(s));

    if (surfacesToRender.length === 0) return nothing;

    return html`
      <div class="turn-inline-surfaces">
        ${surfacesToRender.map(surface => html`
          <div class="inline-surface-card">
            <div class="inline-surface-hdr">
              <span class="inline-surface-title">[A2UI SURFACE: ${surface.id.toUpperCase()}]</span>
              <button class="surface-close-btn" @click=${() => this.closeSurface(surface.id)}>[X] DISMISS</button>
            </div>
            <div class="inline-surface-body">
              <a2ui-surface .surface=${surface}></a2ui-surface>
            </div>
          </div>
        `)}
      </div>
    `;
  }

  render() {
    return html`
      <div id="app-container">
        <!-- FIXED HEADER (TOP) -->
        <header id="fixed-header">
          <!-- 1. System Info & Operational Readout (Column 1) -->
          <div class="header-left-pane">
            <div class="header-sysinfo">
              <div class="sysinfo-title-row">
                <span class="sys-badge">[SYS]</span>
                <span class="sys-title">EMERGENCY DIAGNOSTIC AGENT</span>
                <span class="health-badge ${this.systemStatus.health.toLowerCase()}">
                  <span class="pulse-dot ${this.systemStatus.health.toLowerCase()}"></span>
                  HEALTH: ${this.systemStatus.health} [OK]
                </span>
              </div>
              <div class="sysinfo-grid">
                <div class="spec-item"><span class="k">HOST:</span><span class="v">${this.systemStatus.hostname}</span></div>
                <div class="spec-item"><span class="k">OS:</span><span class="v">${this.systemStatus.os}</span></div>
                <div class="spec-item"><span class="k">KERNEL:</span><span class="v">${this.systemStatus.kernel}</span></div>
                <div class="spec-item"><span class="k">UPTIME:</span><span class="v">${this.systemStatus.uptime}</span></div>
              </div>
            </div>

            <!-- Operational Status Readout below System Info -->
            <div class="header-status-panel">
              <div class="status-panel-label">OPERATIONAL STATUS READOUT:</div>
              <div class="status-lcd-bezel">
                <div class="status-lcd-scanline"></div>
                <div class="status-lcd-text">${this.statusBarText}</div>
              </div>
            </div>
          </div>

          <!-- 2. AIDA's Avatar Column (Column 2) -->
          <div class="header-avatar-col">
            <!-- AIDA-AI label at top of avatar -->
            <div class="avatar-name">AIDA-AI</div>

            <div class="avatar-frame">
              <img 
                src="/${this.avatarState}?cb=${this.cacheBuster}" 
                alt="AIDA Avatar" 
                class="avatar-img" 
              />
            </div>

            <!-- Online status under avatar -->
            <div class="avatar-badge" style="color: ${this.avatarLabelColor}">
              <span class="pulse-dot ${this.avatarState === 'error' ? 'error' : this.avatarState.startsWith('think') ? 'thinking' : 'nominal'}"></span>
              ${this.avatarLabelText}
            </div>

            <!-- Two buttons below the status -->
            <div class="header-btns">
              <button class="hdr-btn" @click=${this.clearSession} title="Reset session">[RESET]</button>
              <button class="hdr-btn ${this.showLogs ? 'active' : ''}" @click=${this.toggleLogs} title="Toggle logs">[LOGS]</button>
            </div>
          </div>
        </header>

        <!-- FREE CANVAS: Scrollable Conversation Stream -->
        <main id="canvas-viewport">
          ${this.turns.length === 1 && this.turns[0].id === 'turn-init' ? html`
            <div class="empty-state">
              <div class="empty-banner">--- AIDA TERMINAL SESSION READY ---</div>
              <div class="empty-hint">State your emergency below or select a diagnostic probe:</div>
              <div class="quick-prompts">
                <button class="quick-btn" @click=${() => this.sendMessage('Check system CPU usage and top active processes')}>&gt; Probe CPU & Processes</button>
                <button class="quick-btn" @click=${() => this.sendMessage('Show system memory and swap allocation')}>&gt; Probe Memory Allocation</button>
                <button class="quick-btn" @click=${() => this.sendMessage('Check storage volumes and disk space usage')}>&gt; Probe Storage Volumes</button>
                <button class="quick-btn" @click=${() => this.sendMessage('Analyze network interface throughput')}>&gt; Probe Network Throughput</button>
              </div>
            </div>
          ` : nothing}

          ${this.turns.map(turn => this.renderTurn(turn))}
        </main>

        <!-- DIAGNOSTIC LOG DRAWER (OPTIONAL) -->
        ${this.showLogs ? html`
          <div id="diagnostic-drawer">
            <div class="drawer-hdr">
              <span>DIAGNOSTIC LOG STREAM</span>
              <button class="hdr-btn" @click=${this.toggleLogs}>[X] CLOSE</button>
            </div>
            <div class="drawer-body" id="log-window">
              ${this.logs.map(log => html`
                <div class="log-entry ${log.type}">
                  <span class="log-time">${log.time}</span>
                  <span class="log-content">${log.content}</span>
                </div>
              `)}
            </div>
          </div>
        ` : nothing}

        <!-- PROMPT INPUT BAR (BOTTOM PINNED) -->
        <footer id="input-footer">
          <form id="user-input" @submit=${this.handleSubmit}>
            <span id="prompt-symbol">AIDA&gt;</span>
            <input 
              type="text" 
              id="message-text" 
              autocomplete="off" 
              autofocus 
              placeholder="State your emergency... (e.g., 'check cpu usage', 'show logs', 'find large tables')" 
              ?disabled=${this.isStreaming}
            />
            <button type="submit" id="submit-btn" ?disabled=${this.isStreaming}>[TRANSMIT]</button>
          </form>
        </footer>
      </div>
    `;
  }
}
