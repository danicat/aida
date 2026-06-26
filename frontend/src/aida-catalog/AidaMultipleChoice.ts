import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaMultipleChoiceApi = {
    name: 'AidaMultipleChoice',
    schema: z.object({
        options: z.array(z.string()),
        selectedValues: z.array(z.string()),
        onChange: z.any()
    })
};

@customElement('aida-multiple-choice')
export class AidaMultipleChoiceElement extends A2uiLitElement<typeof AidaMultipleChoiceApi> {
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
        .checkbox {
            width: 16px;
            height: 16px;
            border: 2px solid var(--pc98-green);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 14px;
            color: var(--pc98-black, #000);
        }
        .checkbox.selected {
            background-color: var(--pc98-green);
        }
        .checkbox.selected::after {
            content: 'x';
            font-family: inherit;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaMultipleChoiceApi);
    }

    private toggleSelection(opt: string) {
        const props = this.controller.props;
        if (!props || !props.onChange || typeof props.onChange !== 'function') return;

        const current = new Set(props.selectedValues);
        if (current.has(opt)) {
            current.delete(opt);
        } else {
            current.add(opt);
        }
        props.onChange({ selectedValues: Array.from(current) });
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <div class="select-container">
                ${props.options.map((opt: string) => html`
                    <div class="option" @click=${() => this.toggleSelection(opt)}>
                        <div class="checkbox ${props.selectedValues.includes(opt) ? 'selected' : ''}"></div>
                        <span>${opt}</span>
                    </div>
                `)}
            </div>
        `;
    }
}

export const AidaMultipleChoice: LitComponentApi = {
    ...AidaMultipleChoiceApi,
    tagName: 'aida-multiple-choice'
};
