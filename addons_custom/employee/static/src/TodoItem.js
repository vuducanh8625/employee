/** @odoo-module **/

import { Component } from "@odoo/owl";

export class TodoItem extends Component {
    static template = "employee.TodoItem";
    static props = {
        todo: {
            type: Object,
            shape: {
                id: Number,
                description: String,
                isCompleted: Boolean,
            },
        },
        toggleState: Function,
        removeTodo: Function,
    };

    onChangeCheckbox() {
        this.props.toggleState(this.props.todo.id);
    }

    onClickRemove() {
        this.props.removeTodo(this.props.todo.id);
    }
}