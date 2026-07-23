/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";
import { DashboardItem } from "./dashboard_item";
import { DashboardSettingsDialog } from "./dashboard_settings_dialog";
// Import file này chỉ để ĐẢM BẢO nó được load (chạy các dòng
// registry.add() bên trong) - không cần dùng gì từ nó trực tiếp
import "./dashboard_items";

export class ContractDashboard extends Component {
    static template = "employee.ContractDashboard";
    static components = { Layout, DashboardItem };
    static props = {};

    setup() {
        this.display = {
            controlPanel: { "top-left": true },
        };

        this.action = useService("action");
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        this.contractStatistics = useService("employee.contract_statistics");
        this.statistics = useState(this.contractStatistics.loadStatistics());

        // Toàn bộ item đã đăng ký (không đổi khi runtime)
        this.allItems = registry.category("employee_contract_dashboard").getAll();

        // Danh sách id item đang bị ẩn - đọc từ server (res.users), reactive
        // để khi Apply xong, dashboard tự re-render ngay
        this.settings = useState({
            disabledIds: [],
        });

        onWillStart(async () => {
            const result = await this.orm.read(
                "res.users",
                [user.userId],
                ["contract_dashboard_config"]
            );
            const raw = result[0].contract_dashboard_config;
            this.settings.disabledIds = raw ? JSON.parse(raw) : [];
        });
    }

    // Danh sách item THỰC SỰ hiển thị = toàn bộ item trừ đi các id bị ẩn
    get items() {
        return this.allItems.filter(
            (item) => !this.settings.disabledIds.includes(item.id)
        );
    }

    async saveDisabledIds(uncheckedIds) {
        await this.orm.write("res.users", [user.userId], {
            contract_dashboard_config: JSON.stringify(uncheckedIds),
        });
        this.settings.disabledIds = uncheckedIds;
    }

    openSettings() {
        this.dialog.add(DashboardSettingsDialog, {
            items: this.allItems.map((item) => ({
                id: item.id,
                description: item.description,
            })),
            disabledItems: this.settings.disabledIds,
            onApply: (uncheckedIds) => this.saveDisabledIds(uncheckedIds),
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