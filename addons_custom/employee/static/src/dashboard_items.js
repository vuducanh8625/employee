/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { NumberCard } from "./number_card";
import { PieChartCard } from "./pie_chart_card";

const dashboardItemsRegistry = registry.category("employee_contract_dashboard");

dashboardItemsRegistry.add("new_contracts", {
    id: "new_contracts",
    description: _t("Hợp đồng mới tháng này"),
    Component: NumberCard,
    props: (data) => ({
        title: _t("Hợp đồng mới tháng này"),
        value: data.new_contracts,
    }),
});

dashboardItemsRegistry.add("total_salary", {
    id: "total_salary",
    description: _t("Tổng lương (hợp đồng đang chạy)"),
    Component: NumberCard,
    props: (data) => ({
        title: _t("Tổng lương (đang chạy)"),
        value: data.total_salary,
    }),
});

dashboardItemsRegistry.add("average_salary", {
    id: "average_salary",
    description: _t("Lương trung bình"),
    Component: NumberCard,
    props: (data) => ({
        title: _t("Lương trung bình"),
        value: data.average_salary,
    }),
});

dashboardItemsRegistry.add("terminated_contracts", {
    id: "terminated_contracts",
    description: _t("Hợp đồng đã chấm dứt"),
    Component: NumberCard,
    props: (data) => ({
        title: _t("Hợp đồng đã chấm dứt"),
        value: data.terminated_contracts,
    }),
});

dashboardItemsRegistry.add("average_duration_days", {
    id: "average_duration_days",
    description: _t("Số ngày trung bình đã chạy"),
    Component: NumberCard,
    props: (data) => ({
        title: _t("Số ngày TB đã chạy"),
        value: data.average_duration_days,
    }),
});

dashboardItemsRegistry.add("contract_type_distribution", {
    id: "contract_type_distribution",
    description: _t("Phân bố theo loại hợp đồng"),
    Component: PieChartCard,
    size: 2,
    props: (data) => ({
        title: _t("Phân bố theo loại hợp đồng"),
        data: data.contract_type_distribution,
    }),
});