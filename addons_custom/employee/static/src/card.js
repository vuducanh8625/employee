/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class Card extends Component {
    static template = "employee.Card";
    static props = {
        title: String,
        onClick: { type: Function, optional: true },
        slots: {
            type: Object,
            shape: {
                default: { type: Object, optional: true },
            },
        },
    };

    setup() {
        // State này KHÔNG đến từ props, KHÔNG đến từ cha - hoàn toàn
        // nội bộ của Card, không ai bên ngoài biết hay can thiệp được
        this.state = useState({ isOpen: true });
    }

    toggle() {
        this.state.isOpen = !this.state.isOpen;
    }

    onCardClick() {
        if (this.props.onClick) {
            this.props.onClick();
        }
    }
}