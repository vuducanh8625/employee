from odoo import fields, models


class Department(models.Model):
    _name = 'department'

    name = fields.Char(string="Department Name")
    employee_ids = fields.One2many(
        comodel_name='employee',
        inverse_name='department_id',
        string="Employees",
    )