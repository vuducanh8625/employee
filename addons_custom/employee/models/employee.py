from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _name = 'employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Full Name")
    last_name = fields.Char(string="Last Name")
    first_name = fields.Char(string="First Name")
    description = fields.Text(string="Description")
    birth_date = fields.Date(string="Birth Date")
    age = fields.Integer(string="Age", compute='_compute_age', store=True)
    position = fields.Char(string="Position")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    salary = fields.Float(string="Salary")
    employee_id = fields.Char(string="Employee ID", size=6, readonly=True, copy=False)
    sex = fields.Selection([('male', 'Male'), ('female', 'Female'), ('lgbt', 'LGBT')])
    parttime = fields.Boolean(string="Part Time")
    work_hours = fields.Integer(string="Work Hours/Week")
    state = fields.Selection([
        ('draft', 'Đang hoàn thiện'),
        ('done', 'Bàn giao cho khách hàng'),
    ], string="Status", default='draft')
    department_id = fields.Many2one(
        comodel_name='department',
        string="Department",
        ondelete='set null',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Tài khoản người dùng",
        ondelete='set null',
    )
    province_id = fields.Many2one(
        comodel_name='province',
        string="Tỉnh/Thành phố",
        ondelete='set null',
    )
    ward_id = fields.Many2one(
        comodel_name='ward',
        string="Xã/Phường",
        domain="[('province_id', '=', province_id)]",
        ondelete='set null',
    )
    street = fields.Char(string="Địa chỉ chi tiết")
    contract_ids = fields.One2many(
        comodel_name='contract',
        inverse_name='employee_id',
        string="Contracts",
    )
    skill_ids = fields.One2many(
        comodel_name='employee.skill',
        inverse_name='employee_id',
        string="Skills",
    )
    project_ids = fields.One2many(
        comodel_name='employee.project',
        inverse_name='employee_id',
        string="Projects",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('employee_id'):
                vals['employee_id'] = self.env['ir.sequence'].next_by_code(
                    'employee.sequence'
                ) or _('New')
        return super().create(vals_list)

    @api.constrains('employee_id')
    def _check_employee_id(self):
        for rec in self:
            if rec.employee_id:
                if len(rec.employee_id) > 6:
                    raise ValidationError(
                        "Employee ID không được quá 6 ký tự!"
                    )
                duplicate = self.search([
                    ('employee_id', '=', rec.employee_id),
                    ('id', '!=', rec.id),
                ])
                if duplicate:
                    raise ValidationError(
                        "Employee ID '%s' đã tồn tại, vui lòng nhập ID khác!" % rec.employee_id
                    )

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = fields.Date.today()
                age = today.year - rec.birth_date.year
                if (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day):
                    age -= 1
                rec.age = age
            else:
                rec.age = 0

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            parts = self.name.strip().split(' ')
            self.last_name = parts[0]
            self.first_name = ' '.join(parts[1:]) if len(parts) > 1 else False
        else:
            self.last_name = False
            self.first_name = False

    @api.onchange('parttime')
    def _onchange_parttime(self):
        if self.parttime:
            self.work_hours = 20
        else:
            self.work_hours = 40

    def action_handover(self):
        self.state = 'done'

    def action_reset_to_draft(self):
        self.state = 'draft'

    def action_reset(self):
        self.write({
            'name': False,
            'last_name': False,
            'first_name': False,
            'description': False,
            'birth_date': False,
            'position': False,
            'email': False,
            'phone': False,
            'salary': 0.0,
            'employee_id': False,
            'sex': False,
            'parttime': False,
            'work_hours': 0,
            'department_id': False,
            'user_id': False,
            'skill_ids': [(5, 0, 0)],
            'contract_ids': [(5, 0, 0)],
            'project_ids': [(5, 0, 0)],
        })

    @api.onchange('end_date')
    def _onchange_end_date_check(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            warning_result = {
                'warning': {
                    'title': "Ngày kết thúc không hợp lệ",
                    'message': "Ngày kết thúc phải lớn hơn ngày bắt đầu (%s)! "
                               "Vui lòng chọn lại ngày kết thúc." % self.start_date,
                }
            }
            self.end_date = False
            return warning_result