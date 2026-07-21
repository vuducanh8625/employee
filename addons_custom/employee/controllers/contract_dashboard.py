# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request


class ContractDashboardController(http.Controller):

    @http.route('/employee/contract_statistics', type='json', auth='user')
    def contract_statistics(self):
        Contract = request.env['contract']
        today = fields.Date.today()
        first_day_of_month = today.replace(day=1)

        # Hợp đồng mới tháng này (tạo trong tháng hiện tại)
        new_contracts = Contract.search([
            ('create_date', '>=', first_day_of_month),
        ])
        nb_new_contracts = len(new_contracts)
        total_salary_new = sum(new_contracts.mapped('salary'))
        avg_salary_new = total_salary_new / nb_new_contracts if nb_new_contracts else 0

        # Hợp đồng bị chấm dứt/hết hạn tháng này
        ended_contracts = Contract.search([
            ('state', 'in', ['terminated', 'expired']),
            ('write_date', '>=', first_day_of_month),
        ])
        nb_ended_contracts = len(ended_contracts)

        # Thời gian trung bình từ lúc tạo đến lúc chấm dứt/hết hạn (đơn vị: ngày)
        # Lưu ý: đây là ước lượng dựa trên write_date - create_date,
        # vì hiện model chưa lưu lại mốc thời gian đổi state chi tiết.
        durations = []
        for rec in ended_contracts:
            if rec.create_date and rec.write_date:
                delta = rec.write_date - rec.create_date
                durations.append(delta.days)
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            'nb_new_contracts': nb_new_contracts,
            'total_salary_new': total_salary_new,
            'avg_salary_new': round(avg_salary_new, 2),
            'nb_ended_contracts': nb_ended_contracts,
            'avg_duration_days': round(avg_duration, 1),
        }