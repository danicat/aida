import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';


export const AidaSingleSelectApi = {
    name: 'AidaSingleSelect',
    schema: z.object({
        options: z.array(z.string()),
        selectedValue: z.string().optional(),
        onChange: z.any()
    })
};

@customElement('aida-single-select')
export class AidaSingleSelectElement extends A2uiLitElement<typeof AidaSingleSelectApi> {
    static styles = css`
        .select-container {
            display: flex;
            flex-direction: column;
            gap: 5px;
            margin: 10px 0;
            padding: 10px;
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-dark-gray);
        }
        .option {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            color: var(--pc98-fg);
        }
        .option:hover {
            color: var(--pc98-cyan);
        }
        .radio-btn {
            width: 16px;
            height: 16px;
            border: 2px solid var(--pc98-green);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .radio-btn.selected {
            background-color: var(--pc98-green);
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaSingleSelectApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <div class="select-container">
                ${props.options.map((opt: string) => html`
                    <div class="option" @click=${() => props.onChange && typeof props.onChange === 'function' && props.onChange({ value: opt })}>
                        <div class="radio-btn ${props.selectedValue === opt ? 'selected' : ''}"></div>
                        <span>${opt}</span>
                    </div>
                `)}
            </div>
        `;
    }
}

export const AidaSingleSelect: LitComponentApi = {
    ...AidaSingleSelectApi,
    tagName: 'aida-single-select'
};
