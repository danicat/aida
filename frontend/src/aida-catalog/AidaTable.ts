import { z } from 'zod';
import { html, css, nothing } from 'lit';
import { customElement } from 'lit/decorators.js';
import { A2uiLitElement, A2uiController } from '@a2ui/lit/v0_9';
import type { LitComponentApi } from '@a2ui/lit/v0_9';

export const AidaTableApi = {
    name: 'AidaTable',
    schema: z.object({
        columns: z.array(z.string()),
        rows: z.array(z.array(z.union([z.string(), z.number(), z.boolean(), z.null(), z.undefined()])))
    })
};

@customElement('aida-table')
export class AidaTableElement extends A2uiLitElement<typeof AidaTableApi> {
    static styles = css`
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            color: var(--pc98-fg); /* High contrast foreground for table body text */
        }
        th, td {
            border: 1px solid var(--pc98-border);
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: var(--pc98-green); /* High contrast solid green background */
            color: var(--pc98-black); /* Perfect contrast black text */
            font-weight: bold;
        }
        td {
            color: var(--pc98-green); /* Keep cell values green for retro aesthetic */
        }
    `;

    protected createController() {
        return new A2uiController(this, AidaTableApi);
    }

    render() {
        const props = this.controller.props;
        if (!props) return nothing;

        return html`
            <table>
                <thead>
                    <tr>
                        ${props.columns.map((col: string) => html`<th>${col}</th>`)}
                    </tr>
                </thead>
                <tbody>
                    ${props.rows.map(row => html`
                        <tr>
                            ${row.map(cell => html`<td>${cell !== null && cell !== undefined ? String(cell) : ''}</td>`)}
                        </tr>
                    `)}
                </tbody>
            </table>
        `;
    }
}

export const AidaTable: LitComponentApi = {
    ...AidaTableApi,
    tagName: 'aida-table'
};
