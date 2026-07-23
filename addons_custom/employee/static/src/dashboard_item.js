/** @odoo-module **/

import { Component } from "@odoo/owl";

export class DashboardItem extends Component {
    static template = "employee.DashboardItem";
    static props = {
        size: { type: Number, optional: true },
        slots: { type: Object, optional: true },
    };
    static defaultProps = {
        size: 1,
    };

    get width() {
        return `${18 * this.props.size}rem`;
    }
}