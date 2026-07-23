/** @odoo-module **/

import { Component, onWillStart, onMounted, useRef } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class PieChart extends Component {
    static template = "employee.PieChart";
    static props = {
        data: Object, // { labels: [...], values: [...], ids: [...] (optional) }
        onSliceClick: { type: Function, optional: true },
    };

    setup() {
        this.canvasRef = useRef("canvas");

        // Chart.js không load sẵn - chỉ tải khi thực sự có PieChart
        // nào đó cần dùng đến, tránh bắt mọi user tải thư viện thừa
        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
        });

        onMounted(() => {
            this.renderChart();
        });
    }

    renderChart() {
        const labels = this.props.data.labels || [];
        const values = this.props.data.values || [];

        new Chart(this.canvasRef.el, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [
                    {
                        data: values,
                        backgroundColor: [
                            "#4e79a7",
                            "#f28e2b",
                            "#e15759",
                            "#76b7b2",
                            "#59a14f",
                            "#edc948",
                        ],
                    },
                ],
            },
            options: {
                onClick: (event, elements) => {
                    if (elements.length && this.props.onSliceClick) {
                        const index = elements[0].index;
                        this.props.onSliceClick(index);
                    }
                },
            },
        });
    }
}