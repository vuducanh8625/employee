/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { memoize } from "@web/core/utils/functions";

export const contractStatisticsService = {
    start() {
        const loadStatistics = memoize(() => {
            return rpc("/employee/contract_statistics");
        });

        return { loadStatistics };
    },
};

registry.category("services").add("employee.contract_statistics", contractStatisticsService);