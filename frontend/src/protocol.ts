import { HttpAgent, type AgentSubscriber } from '@ag-ui/client';
import type { UserMessage } from '@ag-ui/core';

export interface ProtocolCallbacks {
  onTextDelta: (delta: string) => void;
  onToolStart: (toolName: string, callId?: string) => void;
  onToolArgsDelta?: (delta: string, callId?: string) => void;
  onToolResult?: (result: any, callId?: string) => void;
  onA2uiOperations: (ops: any[]) => void;
  onStatusChange: (statusText: string) => void;
  onRunStarted: () => void;
  onRunFinished: () => void;
  onError: (err: string) => void;
  onLog?: (log: string) => void;
}

// Canonical AG-UI HttpAgent (browser-native)
const httpAgent = new HttpAgent({
  url: '/api/agent',
  threadId: 'web_thread',
});

/**
 * Streams agent response via canonical AG-UI HttpAgent.
 */
export async function streamAgentResponse(
  query: string,
  callbacks: ProtocolCallbacks,
  signal?: AbortSignal
): Promise<void> {
  callbacks.onRunStarted();
  callbacks.onStatusChange('THINKING...');

  const controller = new AbortController();
  if (signal) {
    signal.addEventListener('abort', () => {
      controller.abort();
      httpAgent.abortRun();
    });
  }

  const userMsg: UserMessage = {
    id: crypto.randomUUID(),
    role: 'user',
    content: query,
  };
  httpAgent.addMessage(userMsg);

  const subscriber: AgentSubscriber = {
    onRunStartedEvent: () => {
      callbacks.onRunStarted();
      callbacks.onStatusChange('PROCESSING QUERY...');
    },
    onTextMessageStartEvent: () => {
      callbacks.onStatusChange('TRANSMITTING RESPONSE...');
    },
    onTextMessageContentEvent: ({ event }) => {
      const delta = event.delta;
      if (!delta) return;
      // Strip any stray <a2ui-json> or <a2ui> tags if present in conversational text stream
      const cleanDelta = delta.replace(/<\/?a2ui(?:-json)?[^>]*>/gi, '');
      if (cleanDelta) {
        callbacks.onTextDelta(cleanDelta);
      }
    },
    onToolCallStartEvent: ({ event }) => {
      callbacks.onToolStart(event.toolCallName, event.toolCallId);
      if (event.toolCallName.includes('osquery')) {
        callbacks.onStatusChange('EXECUTING QUERY: SELECT...');
      } else if (event.toolCallName.includes('skill')) {
        callbacks.onStatusChange('LOADING SKILL...');
      } else {
        callbacks.onStatusChange(`EXECUTING: ${event.toolCallName.toUpperCase()}...`);
      }
    },
    onToolCallArgsEvent: ({ event }) => {
      if (callbacks.onToolArgsDelta) {
        callbacks.onToolArgsDelta(event.delta || '', event.toolCallId);
      }
    },
    onToolCallResultEvent: ({ event }) => {
      if (callbacks.onToolResult) {
        callbacks.onToolResult(event.content, event.toolCallId);
      }
      // Fixed schema tool detection (e.g. show_ui_controls or diagnostic tools)
      extractAndDispatchA2ui(event.content, callbacks);
    },
    onActivitySnapshotEvent: ({ event }) => {
      if (event.activityType === 'a2ui-surface') {
        const ops = (event.content as any)?.a2ui_operations;
        if (Array.isArray(ops) && ops.length > 0) {
          callbacks.onA2uiOperations(ops);
        }
      } else if (event.content) {
        extractAndDispatchA2ui(event.content, callbacks);
      }
    },
    onCustomEvent: ({ event }) => {
      if (event.name === 'a2ui' || (event as any).type === 'a2ui') {
        const ops = Array.isArray((event as any).content) ? (event as any).content : [(event as any).content];
        callbacks.onA2uiOperations(ops);
      }
    },
    onRunFinishedEvent: () => {
      callbacks.onRunFinished();
      callbacks.onStatusChange('IDLE - STANDBY');
    },
    onRunErrorEvent: ({ event }) => {
      callbacks.onError(event.message || 'Run error occurred');
      callbacks.onStatusChange('ERROR - RUN FAILED');
    },
  };

  try {
    await httpAgent.runAgent(
      {
        forwardedProps: {
          injectA2UITool: true,
          defaultCatalogId: 'aida_custom',
        },
        abortController: controller,
      },
      subscriber
    );
  } catch (err: any) {
    if (err.name === 'AbortError' || controller.signal.aborted) {
      callbacks.onStatusChange('IDLE - OPERATION CANCELLED');
      callbacks.onRunFinished();
      return;
    }
    const message = err?.message || String(err);
    callbacks.onError(message);
    callbacks.onStatusChange('ERROR - TRANSMISSION INTERRUPTED');
  }
}

/**
 * Extracts A2UI operations from tool results or activity payloads.
 */
export function extractAndDispatchA2ui(payload: any, callbacks: ProtocolCallbacks) {
  if (!payload) return;

  if (typeof payload === 'string') {
    try {
      payload = JSON.parse(payload);
    } catch {
      return;
    }
  }

  // Array of A2UI messages directly
  if (Array.isArray(payload)) {
    if (payload.some(item => item && (item.createSurface || item.updateComponents || item.updateDataModel || item.deleteSurface))) {
      callbacks.onA2uiOperations(payload);
    }
    return;
  }

  if (typeof payload === 'object') {
    if (Array.isArray(payload.a2ui_operations)) {
      callbacks.onA2uiOperations(payload.a2ui_operations);
      return;
    }

    if (payload.createSurface || payload.updateComponents || payload.updateDataModel || payload.deleteSurface) {
      callbacks.onA2uiOperations([payload]);
      return;
    }

    if (payload.a2ui) {
      const ops = Array.isArray(payload.a2ui) ? payload.a2ui : [payload.a2ui];
      callbacks.onA2uiOperations(ops);
      return;
    }
  }
}
