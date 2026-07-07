from odoo import fields, models


class ContractSalaryHistory(models.Model):
    _name = 'contract.salary.history'
    _description = 'Lịch sử thay đổi lương'
    _order = 'start_date asc'

    contract_id = fields.Many2one(
        comodel_name='contract',
        string="Hợp đồng",
        ondelete='cascade',
    )
    salary = fields.Float(string="Lương")
    start_date = fields.Date(string="Ngày bắt đầu")
    end_date = fields.Date(string="Ngày kết thúc")