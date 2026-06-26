import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaSliderApi = {
    name: 'AidaSlider',
    schema: z.object({
        label: z.string(),
        min: z.number(),
        max: z.number(),
        value: z.number(),
        step: z.number().optional(),
        cssVar: z.string().optional(),
        unit: z.string().optional(),
        onChange: z.any().optional()
    })
};

@customElement('aida-slider')
export class AidaSliderElement extends A2uiLitElement<typeof AidaSliderApi> {
    static styles = css`
        .slider-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin: 10px 0;
            padding: 12px;
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-dark-gray);
        }
        .slider-header {
            display: flex;
            justify-content: space-between;
            color: var(--pc98-green);
            font-size: calc(var(--aida-font-size-base, 24px) * 0.75);
            text-shadow: 0 0 5px var(--pc98-green);
        }
        .slider-wrapper {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        input[type="range"] {
            -webkit-appearance: none;
            appearance: none;
            flex-grow: 1;
            height: 8px;
            background: #000011;
            border: 2px solid var(--pc98-border);
            outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 24px;
            background: var(--pc98-cyan);
            border: 1px solid #ffffff;
            cursor: pointer;
        }
        input[type="range"]::-moz-range-thumb {
            width: 16px;
            height: 24px;
            background: var(--pc98-cyan);
            border: 1px solid #ffffff;
            cursor: pointer;
        }
        .slider-value {
            color: var(--pc98-cyan);
            font-size: calc(var(--aida-font-size-base, 24px) * 0.83);
            min-width: 55px;
            text-align: right;
        }
    `;

    @state()
    private _localValue: number | null = null;

    protected createController() {
        return new A2uiController(this, AidaSliderApi);
    }

    private handleInput(e: Event) {
        const input = e.target as HTMLInputElement;
        const val = Number(input.value);
        this._localValue = val;

        const props = this.controller.props;
        if (!props) return;

        if (props.cssVar) {
            const finalValue = `${val}${props.unit || ''}`;
            document.documentElement.style.setProperty(props.cssVar, finalValue);
        } else if (props.onChange && typeof props.onChange === 'function') {
            props.onChange({ value: val });
        }
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        let currentValue = this._localValue !== null ? this._localValue : props.value;
        if (props.cssVar) {
            const rawStyle = document.documentElement.style.getPropertyValue(props.cssVar).trim();
            if (rawStyle) {
                const parsed = parseFloat(rawStyle);
                if (!isNaN(parsed)) {
                    currentValue = parsed;
                }
            }
        }

        return html`
            <div class="slider-container">
                <div class="slider-header">
                    <span>${props.label}</span>
                </div>
                <div class="slider-wrapper">
                    <input 
                        type="range" 
                        min=${props.min} 
                        max=${props.max} 
                        step=${props.step ?? 1} 
                        .value=${currentValue}
                        @input=${(e: Event) => this.handleInput(e)}
                    />
                    <span class="slider-value">${currentValue}${props.unit || ''}</span>
                </div>
            </div>
        `;
    }
}

export const AidaSlider: LitComponentApi = {
    ...AidaSliderApi,
    tagName: 'aida-slider'
};
