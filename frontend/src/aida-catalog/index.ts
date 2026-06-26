import { Catalog } from '@a2ui/web_core/v0_9';
import { BASIC_FUNCTIONS } from '@a2ui/web_core/v0_9/basic_catalog';
import { basicCatalog } from '@a2ui/lit/v0_9';
import { AidaTable } from './AidaTable.js';
import { AidaCard } from './AidaCard.js';
import { AidaButton } from './AidaButton.js';
import { AidaMetricBar } from './AidaMetricBar.js';
import { AidaLogViewer } from './AidaLogViewer.js';
import { AidaBarChart } from './AidaBarChart.js';
import { AidaPieChart } from './AidaPieChart.js';
import { AidaLineChart } from './AidaLineChart.js';
import { AidaCpuMeter } from './AidaCpuMeter.js';
import { AidaMemoryGauge } from './AidaMemoryGauge.js';
import { AidaDiskUsage } from './AidaDiskUsage.js';
import { AidaNetworkThroughput } from './AidaNetworkThroughput.js';
import { AidaSingleSelect } from './AidaSingleSelect.js';
import { AidaMultipleChoice } from './AidaMultipleChoice.js';
import { AidaTextBox } from './AidaTextBox.js';

export const aidaCustomCatalog = new Catalog(
    'aida_custom', 
    [
        ...Array.from(basicCatalog.components.values()),
        AidaTable, AidaCard, AidaButton, AidaMetricBar,
        AidaLogViewer, AidaBarChart, AidaPieChart, AidaLineChart,
        AidaCpuMeter, AidaMemoryGauge, AidaDiskUsage, AidaNetworkThroughput,
        AidaSingleSelect, AidaMultipleChoice, AidaTextBox
    ],
    BASIC_FUNCTIONS
);
