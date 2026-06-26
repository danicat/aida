import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaDiskUsageApi = {
    name: 'AidaDiskUsage',
    schema: z.object({
        mounts: z.array(z.object({
            path: z.string(),
            used: z.number(),
            total: z.number(),
            unit: z.string().optional()
        })),
        unit: z.string().optional()
    })
};

@customElement('aida-disk-usage')
export class AidaDiskUsageElement extends A2uiLitElement<typeof AidaDiskUsageApi> {
    static styles = css`
        .disk-container {
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-black, #000000);
            padding: 12px;
            margin: 10px 0;
            width: 100%;
        }
        .disk-title {
            color: var(--pc98-green);
            margin-bottom: 12px;
            border-bottom: 1px dashed var(--pc98-border);
            padding-bottom: 5px;
            font-size: 1.1em;
            font-weight: bold;
        }
        .mount-row {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 8px;
            width: 100%;
        }
        .mount-path {
            color: var(--pc98-cyan);
            flex: 1 1 160px;
            min-width: 100px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .mount-bar-bg {
            flex: 1.5 2 150px;
            height: 14px;
            background-color: var(--pc98-black, #000);
            border: 1px solid var(--pc98-border);
            max-width: 450px;
        }
        .mount-bar-fg {
            height: 100%;
            background-color: var(--pc98-green);
            transition: width 0.5s ease-in-out;
        }
        .mount-bar-fg.high { background-color: var(--pc98-red); }
        
        .mount-value {
            color: var(--pc98-fg);
            flex: 0 0 130px;
            text-align: right;
            font-size: 0.9em;
            font-family: 'VT323', monospace;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaDiskUsageApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        const formatPair = (used: number, total: number, itemUnit?: string) => {
            const displayUnit = itemUnit || props.unit;
            const formattedUsed = used.toFixed(used % 1 === 0 ? 0 : 1);
            const formattedTotal = total.toFixed(total % 1 === 0 ? 0 : 1);
            return displayUnit ? `${formattedUsed} ${displayUnit} / ${formattedTotal} ${displayUnit}` : `${formattedUsed} / ${formattedTotal}`;
        };

        return html`
            <div class="disk-container">
                <div class="disk-title">STORAGE VOLUMES</div>
                ${props.mounts.map(mount => {
                    const percentage = mount.total > 0 ? (mount.used / mount.total) * 100 : 0;
                    const clamped = Math.max(0, Math.min(100, percentage));
                    return html`
                        <div class="mount-row">
                            <div class="mount-path" title="${mount.path}">${mount.path}</div>
                            <div class="mount-bar-bg">
                                <div class="mount-bar-fg ${clamped > 90 ? 'high' : ''}" style="width: ${clamped}%"></div>
                            </div>
                            <div class="mount-value">${formatPair(mount.used, mount.total, mount.unit)}</div>
                        </div>
                    `;
                })}
            </div>
        `;
    }
}

export const AidaDiskUsage: LitComponentApi = {
    ...AidaDiskUsageApi,
    tagName: 'aida-disk-usage'
};
