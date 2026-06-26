import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaMemoryGaugeApi = {
    name: 'AidaMemoryGauge',
    schema: z.object({
        used: z.number(),
        total: z.number(),
        unit: z.string().optional()
    })
};

@customElement('aida-memory-gauge')
export class AidaMemoryGaugeElement extends A2uiLitElement<typeof AidaMemoryGaugeApi> {
    static styles = css`
        .mem-container {
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-dark-gray);
            padding: 12px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            gap: 15px;
            width: 100%;
        }
        .mem-label {
            color: var(--pc98-green);
            font-size: 1.2em;
            text-shadow: 0 0 5px var(--pc98-green);
            flex: 0 0 60px;
        }
        .gauge-bg {
            flex: 1.5 2 150px;
            height: 24px;
            background-color: var(--pc98-black, #000);
            border: 2px inset var(--pc98-border);
            position: relative;
            max-width: 450px;
        }
        .gauge-fg {
            height: 100%;
            background-color: var(--pc98-cyan);
            transition: width 0.5s;
        }
        .gauge-fg.high { background-color: var(--pc98-red); }
        .gauge-fg.med { background-color: var(--pc98-amber); }
        
        .mem-value {
            color: var(--pc98-fg);
            flex: 0 0 150px;
            text-align: right;
            font-family: 'VT323', monospace;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaMemoryGaugeApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        const percentage = props.total > 0 ? (props.used / props.total) * 100 : 0;
        const clamped = Math.max(0, Math.min(100, percentage));
        const stateClass = clamped > 85 ? 'high' : clamped > 60 ? 'med' : '';

        const formatPair = (used: number, total: number) => {
            const displayUnit = props.unit;
            const formattedUsed = used.toFixed(used % 1 === 0 ? 0 : 1);
            const formattedTotal = total.toFixed(total % 1 === 0 ? 0 : 1);
            return displayUnit ? `${formattedUsed} ${displayUnit} / ${formattedTotal} ${displayUnit}` : `${formattedUsed} / ${formattedTotal}`;
        };

        return html`
            <div class="mem-container">
                <div class="mem-label">MEM</div>
                <div class="gauge-bg">
                    <div class="gauge-fg ${stateClass}" style="width: ${clamped}%"></div>
                </div>
                <div class="mem-value">${formatPair(props.used, props.total)}</div>
            </div>
        `;
    }
}

export const AidaMemoryGauge: LitComponentApi = {
    ...AidaMemoryGaugeApi,
    tagName: 'aida-memory-gauge'
};
