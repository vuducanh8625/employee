/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { reactive } from "@odoo/owl";

// Để TEST cho nhanh, dùng 10 giây. Khi dùng thật, đổi thành:
// const RELOAD_INTERVAL = 10 * 60 * 1000; // 10 phút
const RELOAD_INTERVAL = 10 * 1000;

const contractStatisticsService = {
    start(env) {
        // reactive - GIỐNG useState nhưng KHÔNG gắn với component nào.
        // Object này sống suốt đời ứng dụng, độc lập với việc Dashboard
        // component có đang được mount hay không.
        const statistics = reactive({});

        async function fetchAndUpdate() {
            const result = await rpc("/employee/contract_statistics");
            // Cập nhật NGAY TRÊN object cũ (Object.assign), không tạo
            // object mới - đúng yêu cầu "update the reactive object in
            // place" để mọi component đang useState() object này thấy
            // thay đổi ngay lập tức
            Object.assign(statistics, result);
        }

        let started = false;

        function loadStatistics() {
            if (!started) {
                started = true;
                // Gọi lần đầu ngay (không cần await ở đây - chạy ngầm,
                // statistics ban đầu trả về rỗng, sẽ tự điền dữ liệu
                // sau khi fetch xong nhờ reactivity)
                fetchAndUpdate();
                // Rồi cứ mỗi RELOAD_INTERVAL lại tự làm mới, bất kể
                // Dashboard có đang mở hay không
                setInterval(fetchAndUpdate, RELOAD_INTERVAL);
            }
            // Luôn trả về ĐÚNG 1 object duy nhất này - dù gọi
            // loadStatistics() bao nhiêu lần từ bao nhiêu component
            return statistics;
        }

        return {
            loadStatistics,
        };
    },
};

registry.category("services").add("employee.contract_statistics", contractStatisticsService);