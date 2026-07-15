/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class Counter extends Component {
    static template = "employee.Counter";
    static props = {
        onChange: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({ value: 0 });
    }

    increment() {
        this.state.value = this.state.value + 1;
        // Nếu cha có đưa hàm onChange xuống thì báo tin cho cha
        if (this.props.onChange) {
            this.props.onChange();
        }
    }
}