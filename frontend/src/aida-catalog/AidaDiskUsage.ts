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
            total: z.number()
        }))
    })
};

@customElement('aida-disk-usage')
export class AidaDiskUsageElement extends A2uiLitElement<typeof AidaDiskUsageApi> {
    static styles = css`
        .disk-container {
            border: 2px solid var(--pc98-border);
            background-color: var(--pc98-black, #000000);
            padding: 10px;
            margin: 10px 0;
        }
        .disk-title {
            color: var(--pc98-green);
            margin-bottom: 10px;
            border-bottom: 1px dashed var(--pc98-border);
            padding-bottom: 5px;
        }
        .mount-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 5px;
        }
        .mount-path {
            color: var(--pc98-cyan);
            width: 80px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .mount-bar-bg {
            flex-grow: 1;
            height: 15px;
            background-color: var(--pc98-black, #000);
            border: 1px solid var(--pc98-border);
        }
        .mount-bar-fg {
            height: 100%;
            background-color: var(--pc98-green);
        }
        .mount-bar-fg.high { background-color: var(--pc98-red); }
        
        .mount-value {
            color: var(--pc98-fg);
            width: 100px;
            text-align: right;
            font-size: 0.9em;
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaDiskUsageApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        const formatGB = (bytes: number) => (bytes / (1024 * 1024 * 1024)).toFixed(1) + 'G';

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
                            <div class="mount-value">${formatGB(mount.used)}/${formatGB(mount.total)}</div>
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
