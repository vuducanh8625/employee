# -*- coding: utf-8 -*-
from datetime import date

from odoo import http
from odoo.http import request


class EmployeeContractDashboardController(http.Controller):

    @http.route('/employee/contract_statistics', type='json', auth='user')
    def contract_statistics(self):
        Contract = request.env['contract']

        today = date.today()
        month_start = today.replace(day=1)

        # Hợp đồng mới tạo trong tháng này (dựa theo start_date)
        new_contracts = Contract.search_count([
            ('start_date', '>=', month_start.strftime('%Y-%m-%d')),
            ('start_date', '<=', today.strftime('%Y-%m-%d')),
        ])

        running_contracts = Contract.search([('state', '=', 'running')])
        total_salary = sum(running_contracts.mapped('total_salary'))
        average_salary = (
            total_salary / len(running_contracts) if running_contracts else 0
        )

        terminated_contracts = Contract.search_count([
            ('state', '=', 'terminated'),
        ])

        # Số ngày trung bình mà các hợp đồng đang chạy đã trải qua
        if running_contracts:
            total_days = sum(
                (today - c.start_date).days
                for c in running_contracts if c.start_date
            )
            average_duration_days = total_days / len(running_contracts)
        else:
            average_duration_days = 0

        # Phân bố theo loại hợp đồng - dùng cho pie chart
        type_groups = Contract.read_group(
            [('state', '=', 'running')],
            ['contract_type_id'],
            ['contract_type_id'],
        )
        labels = []
        values = []
        type_ids = []
        for g in type_groups:
            if g['contract_type_id']:
                type_ids.append(g['contract_type_id'][0])
                labels.append(g['contract_type_id'][1])
            else:
                type_ids.append(False)
                labels.append('Chưa xác định')
            values.append(g['contract_type_id_count'])

        return {
            'new_contracts': new_contracts,
            'total_salary': total_salary,
            'average_salary': round(average_salary, 2),
            'terminated_contracts': terminated_contracts,
            'average_duration_days': round(average_duration_days, 1),
            'contract_type_distribution': {
                'labels': labels,
                'values': values,
                'ids': type_ids,
            },
        }