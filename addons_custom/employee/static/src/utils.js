/** @odoo-module **/

import { useRef, onMounted } from "@odoo/owl";

/**
 * Custom hook: tự động focus vào 1 phần tử HTML ngay khi component
 * được mounted (gắn vào DOM thật).
 *
 * @param {string} refName - tên đặt trong t-ref="..." của template
 * @returns {object} ref object, có thể dùng .el nếu cần truy cập thêm
 */
export function useAutofocus(refName) {
    const ref = useRef(refName);
    onMounted(() => {
        if (ref.el) {
            ref.el.focus();
        }
    });
    return ref;
}