/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class Counter extends Component {
    static template = "employee.Counter";
    static props = {
        // onChange nhận giá trị mới của counter, không chỉ "báo tin suông"
        // để cha có thể xử lý đúng dù logic tăng/giảm sau này thay đổi
        onChange: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({ value: 0 });
    }

    increment() {
        this.state.value = this.state.value + 1;
        // Báo giá trị mới lên cha (nếu cha có truyền callback xuống)
        if (this.props.onChange) {
            this.props.onChange(this.state.value);
        }
    }
}