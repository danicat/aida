import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaMetricBarApi = {
    name: 'AidaMetricBar',
    schema: z.object({
        label: z.string(),
        value: z.number(),
        max: z.number()
    })
};

@customElement('aida-metric-bar')
export class AidaMetricBarElement extends A2uiLitElement<typeof AidaMetricBarApi> {
    static styles = css`
        .metric-container {
            margin: 10px 0;
            display: flex;
            align-items: center;
            width: 100%;
        }
        .metric-label {
            width: 150px;
            color: var(--pc98-cyan);
            font-weight: bold;
            flex-shrink: 0;
        }
        .metric-bar-bg {
            flex-grow: 1;
            height: 20px;
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-black, #000000);
            margin-right: 15px;
            position: relative;
        }
        .metric-bar-fg {
            height: 100%;
            background-color: var(--pc98-green);
            transition: width 0.5s ease-in-out;
        }
        .metric-value {
            width: 80px;
            text-align: right;
            color: var(--pc98-green);
            font-weight: bold;
            flex-shrink: 0;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaMetricBarApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        const percentage = Math.min(100, Math.max(0, (props.value / props.max) * 100));

        return html`
            <div class="metric-container">
                <div class="metric-label">${props.label}</div>
                <div class="metric-bar-bg">
                    <div class="metric-bar-fg" style="width: ${percentage}%"></div>
                </div>
                <div class="metric-value">${props.value}/${props.max}</div>
            </div>
        `;
    }
}

export const AidaMetricBar: LitComponentApi = {
    ...AidaMetricBarApi,
    tagName: 'aida-metric-bar'
};
