/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { TodoItem } from "./TodoItem";
import { useAutofocus } from "./utils";

export class TodoList extends Component {
    static template = "employee.TodoList";
    static components = { TodoItem };

    setup() {
        this.todos = useState([]);
        this.nextId = 1;

        // "todoInput" phải khớp CHÍNH XÁC với t-ref="todoInput" trong XML
        this.inputRef = useAutofocus("todoInput");
    }

    addTodo(ev) {
        // keyCode 13 = phím Enter
        if (ev.keyCode !== 13) {
            return;
        }

        const description = ev.target.value.trim();

        // Bonus: không làm gì nếu input rỗng (hoặc chỉ toàn khoảng trắng)
        if (!description) {
            return;
        }

        this.todos.push({
            id: this.nextId,
            description: description,
            isCompleted: false,
        });
        this.nextId = this.nextId + 1;

        // Xóa trắng input sau khi thêm xong
        ev.target.value = "";
    }

    toggleState(todoId) {
        const todo = this.todos.find((t) => t.id === todoId);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }

    removeTodo(todoId) {
        const index = this.todos.findIndex((t) => t.id === todoId);
        if (index >= 0) {
            this.todos.splice(index, 1);
        }
    }
}