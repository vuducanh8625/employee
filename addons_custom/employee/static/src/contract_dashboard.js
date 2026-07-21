/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { DashboardItem } from "./dashboard_item";
import { PieChart } from "./pie_chart";

export class ContractDashboard extends Component {
    static template = "employee.ContractDashboard";
    static components = { Layout, DashboardItem, PieChart };
    static props = {};

    setup() {
        this.display = {
            controlPanel: { "top-left": true },
        };

        this.action = useService("action");
        this.contractStatistics = useService("employee.contract_statistics");
        this.statistics = useState({});

        // TODO: thay bằng dữ liệu thật khi có model lưu size áo/đơn hàng
        this.tshirtData = {
            labels: ["S", "M", "L", "XL", "XXL"],
            values: [12, 25, 30, 18, 7],
        };

        onWillStart(async () => {
            const result = await this.contractStatistics.loadStatistics();
            Object.assign(this.statistics, result);
        });
    }

    openCustomers() {
        this.action.doAction("base.action_partner_form");
    }

    openLeads() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Leads",
            res_model: "crm.lead",
            views: [[false, "list"], [false, "form"]],
        });
    }
}
registry.category("actions").add("employee_contract_owl_dashboard", ContractDashboard);