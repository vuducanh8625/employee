from odoo import fields, models


class ContractType(models.Model):
    _name = 'contract.type'
    _description = 'Loại hợp đồng'

    name = fields.Char(string="Tên loại hợp đồng", required=True)
    default_duration = fields.Integer(
        string="Thời hạn mặc định (tháng)",
        default=12,
        help="Số tháng mặc định để tự động đề xuất Ngày kết thúc khi tạo hợp đồng.",
    )