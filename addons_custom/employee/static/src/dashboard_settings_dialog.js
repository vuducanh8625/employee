/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class DashboardSettingsDialog extends Component {
    static template = "employee.DashboardSettingsDialog";
    static components = { Dialog };
    static props = {
        items: Array,          // [{ id, description }, ...] - toàn bộ item hiện có
        disabledItems: Array,  // [id, ...] - các item đang bị ẩn (đọc từ localStorage)
        onApply: Function,     // callback khi bấm Apply
        close: Function,       // do dialog service tự truyền vào
    };

    setup() {
        // checked = true nghĩa là item đang được HIỂN THỊ (tick trên UI)
        this.state = useState({
            checked: Object.fromEntries(
                this.props.items.map((item) => [
                    item.id,
                    !this.props.disabledItems.includes(item.id),
                ])
            ),
        });
    }

    toggle(id) {
        this.state.checked[id] = !this.state.checked[id];
    }

    onApply() {
        const uncheckedIds = this.props.items
            .filter((item) => !this.state.checked[item.id])
            .map((item) => item.id);
        this.props.onApply(uncheckedIds);
        this.props.close();
    }
}