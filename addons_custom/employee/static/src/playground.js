/** @odoo-module **/

import { Component, markup, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Counter } from "./counter";
import { Card } from "./card";

export class Playground extends Component {
    static template = "employee.Playground";
    static props = {};
    static components = { Counter, Card };

    setup() {
        this.unsafeHtmlExample = "<strong>Chữ này không in đậm được</strong> vì bị escape.";
        this.htmlExample = markup(
            "<strong>Chữ này in đậm thật</strong> vì đã qua markup()."
        );

        // Tổng của 2 Counter - ban đầu là 2, mỗi lần 1 trong 2 Counter
        // tăng thì Counter đó "báo tin" về đây qua onChange
        this.state = useState({ sum: 2 });
    }

    incrementSum() {
        this.state.sum = this.state.sum + 1;
    }
}

registry.category("actions").add("employee_owl_playground", Playground);