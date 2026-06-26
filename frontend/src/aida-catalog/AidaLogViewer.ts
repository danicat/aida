import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaLogViewerApi = {
    name: 'AidaLogViewer',
    schema: z.object({
        title: z.string().optional(),
        text: z.string()
    })
};

@customElement('aida-log-viewer')
export class AidaLogViewerElement extends A2uiLitElement<typeof AidaLogViewerApi> {
    static styles = css`
        .log-container {
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-black, #000);
            padding: 10px;
            margin: 10px 0;
            height: 200px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--pc98-border) var(--pc98-black, #000);
            font-family: inherit;
        }
        .log-entry {
            margin-bottom: 4px;
            line-height: 1.2;
            word-wrap: break-word;
        }
        .log-entry.error { color: var(--pc98-red); }
        .log-time { color: var(--pc98-cyan); margin-right: 5px; }
        .log-sys { color: var(--pc98-amber); }
        .log-content { color: var(--pc98-fg); }
        .log-entry.error .log-content { color: var(--pc98-red); }
    `;

    protected createController() {
        return new A2uiController(this, AidaLogViewerApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <div class="log-container">
                ${props.title ? html`<div class="log-entry log-sys">[SYS] ${props.title}</div>` : ''}
                ${props.text.split('\n').map(line => html`
                    <div class="log-entry">
                        <span class="log-content">${line}</span>
                    </div>
                `)}
            </div>
        `;
    }
}

export const AidaLogViewer: LitComponentApi = {
    ...AidaLogViewerApi,
    tagName: 'aida-log-viewer'
};
