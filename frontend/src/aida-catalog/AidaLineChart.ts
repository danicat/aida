import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement, query } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export const AidaLineChartApi = {
    name: 'AidaLineChart',
    schema: z.object({
        title: z.string(),
        xAxisLabel: z.string().optional(),
        yAxisLabel: z.string().optional(),
        data: z.array(z.object({
            label: z.string(),
            value: z.number()
        }))
    })
};

@customElement('aida-line-chart')
export class AidaLineChartElement extends A2uiLitElement<typeof AidaLineChartApi> {
    static styles = css`
        .chart-container {
            border: 4px ridge var(--pc98-border);
            background-color: var(--pc98-dark-gray);
            padding: 15px;
            margin: 10px 0;
            display: flex;
            flex-direction: column;
            width: 100%;
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
        .canvas-wrapper {
            position: relative;
            height: 220px;
            width: 100%;
        }
    `;

    private chartInstance: Chart | null = null;

    @query('canvas')
    private canvasElement!: HTMLCanvasElement;

    protected createController() {
        return new A2uiController(this, AidaLineChartApi);
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
        const greenColor = style.getPropertyValue('--pc98-green').trim() || '#55ff55';
        const fgColor = style.getPropertyValue('--pc98-fg').trim() || '#d4d4d4';
        const cyanColor = style.getPropertyValue('--pc98-cyan').trim() || '#00ffff';

        this.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: props.data.map(d => d.label),
                datasets: [{
                    label: props.title,
                    data: props.data.map(d => d.value),
                    borderColor: greenColor,
                    backgroundColor: 'rgba(85, 255, 85, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.2,
                    pointBackgroundColor: cyanColor,
                    pointBorderColor: borderColor,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
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
                },
                scales: {
                    x: {
                        title: props.xAxisLabel ? {
                            display: true,
                            text: props.xAxisLabel,
                            color: cyanColor,
                            font: { family: 'VT323', size: 18 }
                        } : undefined,
                        grid: {
                            color: borderColor,
                            lineWidth: 1
                        },
                        ticks: {
                            color: fgColor,
                            font: { family: 'VT323', size: 18 }
                        }
                    },
                    y: {
                        title: props.yAxisLabel ? {
                            display: true,
                            text: props.yAxisLabel,
                            color: cyanColor,
                            font: { family: 'VT323', size: 18 }
                        } : undefined,
                        grid: {
                            color: borderColor,
                            lineWidth: 1
                        },
                        ticks: {
                            color: fgColor,
                            font: { family: 'VT323', size: 18 }
                        }
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

export const AidaLineChart: LitComponentApi = {
    ...AidaLineChartApi,
    tagName: 'aida-line-chart'
};
