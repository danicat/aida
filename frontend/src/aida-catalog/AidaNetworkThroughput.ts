import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaNetworkThroughputApi = {
    name: 'AidaNetworkThroughput',
    schema: z.object({
        interfaceName: z.string(),
        rx: z.number(),
        tx: z.number()
    })
};

@customElement('aida-network-throughput')
export class AidaNetworkThroughputElement extends A2uiLitElement<typeof AidaNetworkThroughputApi> {
    static styles = css`
        .net-container {
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-dark-gray);
            padding: 10px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .net-title {
            color: var(--pc98-green);
        }
        .net-stats {
            display: flex;
            gap: 20px;
        }
        .stat {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }
        .stat-label {
            color: var(--pc98-cyan);
            font-size: 0.8em;
        }
        .stat-value {
            color: var(--pc98-fg);
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaNetworkThroughputApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        const formatSpeed = (bytesPerSec: number) => {
            if (bytesPerSec > 1024 * 1024) return (bytesPerSec / (1024 * 1024)).toFixed(1) + ' MB/s';
            if (bytesPerSec > 1024) return (bytesPerSec / 1024).toFixed(1) + ' KB/s';
            return bytesPerSec + ' B/s';
        };

        return html`
            <div class="net-container">
                <div class="net-title">NET [${props.interfaceName}]</div>
                <div class="net-stats">
                    <div class="stat">
                        <span class="stat-label">RX (DOWN)</span>
                        <span class="stat-value">${formatSpeed(props.rx)}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">TX (UP)</span>
                        <span class="stat-value">${formatSpeed(props.tx)}</span>
                    </div>
                </div>
            </div>
        `;
    }
}

export const AidaNetworkThroughput: LitComponentApi = {
    ...AidaNetworkThroughputApi,
    tagName: 'aida-network-throughput'
};
