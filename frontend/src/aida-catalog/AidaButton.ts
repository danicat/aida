import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

// Define the schema inline similar to Button.d.ts if needed, or just use z.any() since the action

// Define the schema inline similar to Button.d.ts if needed, or just use z.any() since the action
// will be a function after resolution.
export const AidaButtonApi = {
    name: 'AidaButton',
    schema: z.object({
        label: z.string(),
        action: z.any() // ResolveA2uiProps handles translating this to a function if the JSON matches Action schema
    })
};

@customElement('aida-button')
export class AidaButtonElement extends A2uiLitElement<typeof AidaButtonApi> {
    static styles = css`
        button {
            background-color: var(--pc98-dark-gray);
            color: var(--pc98-green);
            border: 2px solid var(--pc98-green);
            padding: 5px 15px;
            cursor: pointer;
            font-family: inherit;
            font-size: inherit;
            margin: 5px;
        }
        button:hover {
            background-color: var(--pc98-green);
            color: var(--pc98-black);
        }
        button:active {
            border-style: inset;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaButtonApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <button @click=${() => props.action && typeof props.action === 'function' && props.action()}>
                ${props.label}
            </button>
        `;
    }
}

export const AidaButton: LitComponentApi = {
    ...AidaButtonApi,
    tagName: 'aida-button'
};
