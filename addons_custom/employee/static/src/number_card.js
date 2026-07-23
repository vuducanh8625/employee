/** @odoo-module **/

import { Component } from "@odoo/owl";

export class NumberCard extends Component {
    static template = "employee.NumberCard";
    static props = {
        title: String,
        value: [Number, String],
    };
}