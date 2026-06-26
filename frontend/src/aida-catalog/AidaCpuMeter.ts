import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaCpuMeterApi = {
    name: 'AidaCpuMeter',
    schema: z.object({
        cores: z.array(z.number())
    })
};

@customElement('aida-cpu-meter')
export class AidaCpuMeterElement extends A2uiLitElement<typeof AidaCpuMeterApi> {
    static styles = css`
        .cpu-container {
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-dark-gray);
            padding: 10px;
            margin: 10px 0;
        }
        .cpu-title {
            color: var(--pc98-green);
            margin-bottom: 10px;
            text-shadow: 0 0 5px var(--pc98-green);
        }
        .core-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 10px;
        }
        .core {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .core-label {
            color: var(--pc98-cyan);
            width: 35px;
            font-size: 0.9em;
        }
        .core-bar-bg {
            flex-grow: 1;
            height: 12px;
            background-color: var(--pc98-black, #000);
            border: 1px solid var(--pc98-border);
            position: relative;
        }
        .core-bar-fg {
            height: 100%;
            background-color: var(--pc98-green);
            transition: width 0.3s;
        }
        .core-bar-fg.high { background-color: var(--pc98-red); }
        .core-bar-fg.med { background-color: var(--pc98-amber); }
        
        .core-value {
            color: var(--pc98-fg);
            width: 35px;
            text-align: right;
            font-size: 0.9em;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaCpuMeterApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <div class="cpu-container">
                <div class="cpu-title">CPU UTILIZATION</div>
                <div class="core-grid">
                    ${props.cores.map((usage, i) => {
                        const clamped = Math.max(0, Math.min(100, usage));
                        const stateClass = clamped > 80 ? 'high' : clamped > 50 ? 'med' : '';
                        return html`
                            <div class="core">
                                <div class="core-label">CPU${i}</div>
                                <div class="core-bar-bg">
                                    <div class="core-bar-fg ${stateClass}" style="width: ${clamped}%"></div>
                                </div>
                                <div class="core-value">${Math.round(clamped)}%</div>
                            </div>
                        `;
                    })}
                </div>
            </div>
        `;
    }
}

export const AidaCpuMeter: LitComponentApi = {
    ...AidaCpuMeterApi,
    tagName: 'aida-cpu-meter'
};
