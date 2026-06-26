import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement, query } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export const AidaPieChartApi = {
    name: 'AidaPieChart',
    schema: z.object({
        title: z.string(),
        slices: z.array(z.object({
            label: z.string(),
            value: z.number(),
            color: z.string()
        }))
    })
};

@customElement('aida-pie-chart')
export class AidaPieChartElement extends A2uiLitElement<typeof AidaPieChartApi> {
    static styles = css`
        .chart-container {
            display: flex;
            flex-direction: column;
            width: 100%;
            max-width: 500px; /* More compact layout */
            margin: 0 auto; /* Center it */
        }
        .chart-title {
            color: var(--pc98-cyan); /* Better contrast than green/grey */
            text-align: center;
            margin-bottom: 10px;
            font-size: 1.2em;
            font-weight: bold;
            text-shadow: 0 0 5px var(--pc98-cyan);
        }
        .canvas-wrapper {
            position: relative;
            height: 180px; /* More compact height */
            width: 100%;
        }
    `;

    private chartInstance: Chart | null = null;

    @query('canvas')
    private canvasElement!: HTMLCanvasElement;

    protected createController() {
        return new A2uiController(this, AidaPieChartApi);
    }

    updated() {
        this.renderChart();
    }

    disconnectedCallback() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
        super.disconnectedCallback();
    }

    private renderChart() {
        const props = this.controller.props;
        if (!props || !this.canvasElement) return;

        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        const ctx = this.canvasElement.getContext('2d');
        if (!ctx) return;

        const style = getComputedStyle(document.documentElement);
        const borderColor = style.getPropertyValue('--pc98-border').trim() || '#5555aa';
        const fgColor = style.getPropertyValue('--pc98-fg').trim() || '#d4d4d4';

        this.chartInstance = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: props.slices.map(s => s.label),
                datasets: [{
                    data: props.slices.map(s => s.value),
                    backgroundColor: props.slices.map(s => s.color),
                    borderColor: borderColor,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: fgColor,
                            font: { family: 'VT323', size: 18 }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: '#000022',
                        titleColor: '#55ff55',
                        bodyColor: '#00ffff',
                        borderColor: '#5555aa',
                        borderWidth: 2,
                        titleFont: { family: 'VT323', size: 18 },
                        bodyFont: { family: 'VT323', size: 16 }
                    }
                }
            }
        });
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <div class="chart-container">
                <div class="chart-title">${props.title}</div>
                <div class="canvas-wrapper">
                    <canvas></canvas>
                </div>
            </div>
        `;
    }
}

export const AidaPieChart: LitComponentApi = {
    ...AidaPieChartApi,
    tagName: 'aida-pie-chart'
};
