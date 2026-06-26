import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaBarChartApi = {
    name: 'AidaBarChart',
    schema: z.object({
        title: z.string(),
        series: z.array(z.object({
            label: z.string(),
            value: z.number(),
            color: z.string().optional()
        })),
        max: z.number().optional()
    })
};

@customElement('aida-bar-chart')
export class AidaBarChartElement extends A2uiLitElement<typeof AidaBarChartApi> {
    static styles = css`
        .chart-container {
            border: 4px ridge var(--pc98-border);
            background-color: var(--pc98-black, #000000);
            padding: 15px;
            margin: 10px auto;
            display: flex;
            flex-direction: column;
            width: 100%;
            max-width: 600px;
        }
        .chart-title {
            color: var(--pc98-green);
            text-align: center;
            margin-bottom: 15px;
            font-size: 1.3em;
            font-weight: bold;
            border-bottom: 2px dashed var(--pc98-border);
            padding-bottom: 5px;
            text-shadow: 0 0 5px var(--pc98-green);
        }
        .bars-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .bar-row {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .bar-label {
            width: 120px;
            color: var(--pc98-cyan);
            font-weight: bold;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            text-align: left;
        }
        .bar-track {
            flex-grow: 1;
            height: 20px;
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-black, #000000);
            position: relative;
        }
        .bar-fill {
            height: 100%;
            background-color: var(--pc98-green);
            transition: width 0.5s ease-in-out;
        }
        .bar-value {
            width: 80px;
            text-align: right;
            color: var(--pc98-fg);
            font-family: 'VT323', monospace;
            font-weight: bold;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaBarChartApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        // Calculate maximum value to determine fill percentages
        const seriesValues = props.series.map(s => s.value);
        const computedMax = props.max || (seriesValues.length > 0 ? Math.max(...seriesValues) : 1);
        const finalMax = computedMax > 0 ? computedMax : 1;

        return html`
            <div class="chart-container">
                <div class="chart-title">${props.title}</div>
                <div class="bars-list">
                    ${props.series.map(item => {
                        const percentage = Math.min(100, Math.max(0, (item.value / finalMax) * 100));
                        return html`
                            <div class="bar-row">
                                <div class="bar-label" title="${item.label}">${item.label}</div>
                                <div class="bar-track">
                                    <div class="bar-fill" style="width: ${percentage}%; background-color: ${item.color || 'var(--pc98-green)'};"></div>
                                </div>
                                <div class="bar-value">${item.value}</div>
                            </div>
                        `;
                    })}
                </div>
            </div>
        `;
    }
}

export const AidaBarChart: LitComponentApi = {
    ...AidaBarChartApi,
    tagName: 'aida-bar-chart'
};
