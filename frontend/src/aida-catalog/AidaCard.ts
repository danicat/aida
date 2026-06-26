import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaCardApi = {
    name: 'AidaCard',
    schema: z.object({
        title: z.string(),
        body: z.string()
    })
};

@customElement('aida-card')
export class AidaCardElement extends A2uiLitElement<typeof AidaCardApi> {
    static styles = css`
        .card {
            border: 2px solid var(--pc98-border);
            padding: 15px;
            margin: 10px 0;
            background: var(--pc98-dark-gray);
        }
        .title {
            color: var(--pc98-green);
            font-size: 1.3em;
            border-bottom: 2px solid var(--pc98-border);
            padding-bottom: 5px;
            margin-bottom: 12px;
            font-weight: bold;
        }
        .body {
            color: var(--pc98-fg); /* High contrast light grey/white */
            font-size: 1.0em;
        }
        .body p {
            margin: 8px 0;
            line-height: 1.5;
        }
        .body h1, .body h2, .body h3, .body h4, .body h5, .body h6 {
            color: var(--pc98-cyan); /* High contrast cyan for headers */
            margin: 14px 0 8px 0;
            font-weight: bold;
        }
        .body ul {
            margin: 8px 0;
            padding-left: 20px;
            list-style-type: square;
        }
        .body li {
            margin: 5px 0;
        }
        .body code {
            font-family: monospace;
            background: rgba(0, 255, 0, 0.15);
            padding: 2px 5px;
            border-radius: 3px;
            border: 1px solid var(--pc98-green);
            color: var(--pc98-cyan);
        }
        .body strong {
            color: var(--pc98-cyan);
            font-weight: bold;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaCardApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <div class="card">
                <div class="title">${props.title}</div>
                <div class="body" style="white-space: pre-wrap; word-break: break-word;">${props.body || ''}</div>
            </div>
        `;
    }
}

export const AidaCard: LitComponentApi = {
    ...AidaCardApi,
    tagName: 'aida-card'
};
