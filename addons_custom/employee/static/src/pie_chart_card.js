/** @odoo-module **/

import { Component } from "@odoo/owl";
import { PieChart } from "./pie_chart";

export class PieChartCard extends Component {
    static template = "employee.PieChartCard";
    static components = { PieChart };
    static props = {
        title: String,
        data: Object,
    };
}