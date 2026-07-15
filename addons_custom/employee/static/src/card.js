/** @odoo-module **/

import { Component } from "@odoo/owl";

export class Card extends Component {
    static template = "employee.Card";
    static props = {
        title: String,
        content: [String, Object], // Object để chấp nhận cả kết quả của markup()
    };
}