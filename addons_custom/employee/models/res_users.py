# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    contract_dashboard_config = fields.Text(
        string="Cấu hình Dashboard hợp đồng",
        help="Lưu danh sách id các dashboard item bị người dùng ẩn (dạng JSON list).",
    )