from odoo import fields, models


class ContractAllowance(models.Model):
    _name = 'contract.allowance'
    _description = 'Phụ cấp hợp đồng'

    name = fields.Char(string="Tên phụ cấp", required=True)
    amount = fields.Float(string="Số tiền")
    contract_id = fields.Many2one(
        comodel_name='contract',
        string="Hợp đồng",
        ondelete='cascade',
    )