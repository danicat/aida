import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement, query } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaTextBoxApi = {
    name: 'AidaTextBox',
    schema: z.object({
        value: z.string().optional(),
        placeholder: z.string().optional(),
        onChange: z.any()
    })
};

@customElement('aida-text-box')
export class AidaTextBoxElement extends A2uiLitElement<typeof AidaTextBoxApi> {
    static styles = css`
        .textbox-container {
            display: flex;
            margin: 10px 0;
            gap: 10px;
        }
        input {
            flex-grow: 1;
            background-color: var(--pc98-black, #000);
            color: var(--pc98-green);
            border: 2px solid var(--pc98-border);
            padding: 8px;
            font-family: inherit;
            font-size: inherit;
            outline: none;
        }
        input:focus {
            border-color: var(--pc98-green);
        }
        button {
            background-color: var(--pc98-dark-gray);
            color: var(--pc98-green);
            border: 2px solid var(--pc98-green);
            padding: 5px 15px;
            cursor: pointer;
            font-family: inherit;
            font-size: inherit;
        }
        button:hover {
            background-color: var(--pc98-green);
            color: var(--pc98-black, #000);
        }
    `;

    @query('input') inputEl!: HTMLInputElement;

    protected createController() {
        return new A2uiController(this, AidaTextBoxApi);
    }

    private submit() {
        const props = this.controller.props;
        if (props && props.onChange && typeof props.onChange === 'function') {
            props.onChange({ value: this.inputEl.value });
        }
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <div class="textbox-container">
                <input type="text" .value=${props.value || ''} placeholder="${props.placeholder || ''}" @keydown=${(e: KeyboardEvent) => e.key === 'Enter' && this.submit()} />
                <button @click=${this.submit}>SUBMIT</button>
            </div>
        `;
    }
}

export const AidaTextBox: LitComponentApi = {
    ...AidaTextBoxApi,
    tagName: 'aida-text-box'
};
