/** @odoo-module **/

import { Component, markup, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Counter } from "./counter";
import { Card } from "./card";
import { TodoList } from "./TodoList";

export class Playground extends Component {
    static template = "employee.Playground";
    static props = {};
    static components = { Counter, Card, TodoList };

    setup() {
        this.unsafeHtmlExample = "<strong>Chữ này không in đậm được</strong> vì bị escape.";
        this.htmlExample = markup(
            "<strong>Chữ này in đậm thật</strong> vì đã qua markup()."
        );

        this.counterValues = useState({ a: 0, b: 0 });

        // ORM service - "cầu nối" gọi xuống Python model, giống
        // self.env['contract'].search_count(...) nhưng viết từ JS
        this.orm = useService("orm");

        // Số liệu hợp đồng thật, lấy từ database - khởi đầu 0 vì
        // lúc setup() chạy, chưa kịp có dữ liệu (phải chờ onWillStart)
        this.contractStats = useState({
            running: 0,
            expiringSoon: 0,
        });

        // onWillStart chạy TRƯỚC khi component render lần đầu,
        // cho phép await - đợi ORM trả dữ liệu về xong mới vẽ giao diện
        onWillStart(async () => {
            this.contractStats.running = await this.orm.searchCount(
                "contract",
                [["state", "=", "running"]]
            );

            const in30Days = new Date();
            in30Days.setDate(in30Days.getDate() + 30);
            const in30DaysStr = in30Days.toISOString().slice(0, 10);

            this.contractStats.expiringSoon = await this.orm.searchCount(
                "contract",
                [
                    ["state", "=", "running"],
                    ["end_date", "<=", in30DaysStr],
                ]
            );
        });
    }

    onCounterAChange(value) {
        this.counterValues.a = value;
    }

    onCounterBChange(value) {
        this.counterValues.b = value;
    }

    get sum() {
        return this.counterValues.a + this.counterValues.b;
    }
}

registry.category("actions").add("employee_owl_playground", Playground);