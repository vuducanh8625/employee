from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Project(models.Model):
    _name = 'employee.project'

    name = fields.Char(string="Project Name")
    state = fields.Selection([
        ('in_progress', 'Đang hoàn thiện'),
        ('done', 'Bàn giao cho khách hàng'),
    ], string="Status", default='in_progress')
    employee_id = fields.Many2one(
        comodel_name='employee',
        string="Employee",
        ondelete='cascade',
    )

    @api.constrains('state')
    def _check_fulltime_for_handover(self):
        for rec in self:
            if rec.state == 'done' and rec.employee_id.parttime:
                raise ValidationError(
                    "Nhân viên %s đang làm Part Time, không thể bàn giao project!" % rec.employee_id.name
                )

    @api.constrains('name')
    def _check_employee_has_skill(self):
        for rec in self:
            if rec.name and not rec.employee_id.skill_ids:
                raise ValidationError(
                    "Nhân viên %s chưa có kỹ năng nào, không thể tạo project!" % rec.employee_id.name
                )