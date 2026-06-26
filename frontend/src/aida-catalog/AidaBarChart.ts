import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement, query } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

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
        return new A2uiController(this, AidaBarChartApi);
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

        this.chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: props.series.map(s => s.label),
                datasets: [{
                    label: props.title,
                    data: props.series.map(s => s.value),
                    backgroundColor: props.series.map(s => s.color || greenColor),
                    borderColor: borderColor,
                    borderWidth: 2,
                    barPercentage: 0.6
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
                        grid: {
                            color: borderColor,
                            lineWidth: 1
                        },
                        ticks: {
                            color: fgColor,
                            font: { family: 'VT323', size: 18 }
                        },
                        max: props.max
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

export const AidaBarChart: LitComponentApi = {
    ...AidaBarChartApi,
    tagName: 'aida-bar-chart'
};
