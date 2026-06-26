import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaColorPickerApi = {
    name: 'AidaColorPicker',
    schema: z.object({
        label: z.string(),
        value: z.string(),
        cssVar: z.string().optional(),
        onChange: z.any().optional()
    })
};

@customElement('aida-color-picker')
export class AidaColorPickerElement extends A2uiLitElement<typeof AidaColorPickerApi> {
    static styles = css`
        .picker-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin: 10px 0;
            padding: 12px;
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-dark-gray);
        }
        .picker-header {
            color: var(--pc98-green);
            font-size: calc(var(--aida-font-size-base, 24px) * 0.75);
            text-shadow: 0 0 5px var(--pc98-green);
        }
        .picker-body {
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        .swatches {
            display: flex;
            gap: 8px;
        }
        .swatch {
            width: 24px;
            height: 24px;
            border: 2px solid var(--pc98-border);
            cursor: pointer;
            box-sizing: border-box;
        }
        .swatch.selected {
            border-color: #ffffff;
            outline: 2px solid var(--pc98-cyan);
        }
        .custom-color-wrapper {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        input[type="color"] {
            -webkit-appearance: none;
            border: none;
            width: 32px;
            height: 32px;
            cursor: pointer;
            background: none;
            padding: 0;
        }
        input[type="color"]::-webkit-color-swatch-wrapper {
            padding: 0;
        }
        input[type="color"]::-webkit-color-swatch {
            border: 2px solid var(--pc98-border);
        }
        .color-value {
            color: var(--pc98-cyan);
            font-size: calc(var(--aida-font-size-base, 24px) * 0.75);
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaColorPickerApi);
    }

    private updateColor(color: string) {
        const props = this.controller.props;
        if (!props) return;

        if (props.cssVar) {
            document.documentElement.style.setProperty(props.cssVar, color);
        } else if (props.onChange && typeof props.onChange === 'function') {
            props.onChange({ value: color });
        }
        this.requestUpdate();
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        let currentValue = props.value;
        if (props.cssVar) {
            const rawStyle = document.documentElement.style.getPropertyValue(props.cssVar).trim();
            if (rawStyle) {
                currentValue = rawStyle;
            }
        }

        const presetColors = [
            '#55ff55', // PC-98 Green
            '#00ffff', // PC-98 Cyan
            '#ffb700', // PC-98 Amber
            '#ff5555', // PC-98 Red
            '#d4d4d4', // PC-98 FG Gray
            '#000022'  // PC-98 BG Blue
        ];

        return html`
            <div class="picker-container">
                <div class="picker-header">${props.label}</div>
                <div class="picker-body">
                    <div class="swatches">
                        ${presetColors.map(color => html`
                            <div 
                                class="swatch ${currentValue.toLowerCase() === color.toLowerCase() ? 'selected' : ''}" 
                                style="background-color: ${color};"
                                @click=${() => this.updateColor(color)}
                                title=${color}
                            ></div>
                        `)}
                    </div>
                    <div class="custom-color-wrapper">
                        <input 
                            type="color" 
                            .value=${currentValue}
                            @input=${(e: Event) => this.updateColor((e.target as HTMLInputElement).value)}
                        />
                        <span class="color-value">${currentValue.toUpperCase()}</span>
                    </div>
                </div>
            </div>
        `;
    }
}

export const AidaColorPicker: LitComponentApi = {
    ...AidaColorPickerApi,
    tagName: 'aida-color-picker'
};
