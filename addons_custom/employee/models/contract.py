from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Contract(models.Model):
    _name = 'contract'
    _description = 'Hợp đồng'

    name = fields.Char(string="Contract Name")
    code = fields.Char(string="Mã hợp đồng", size=20)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    employee_id = fields.Many2one(
        comodel_name='employee',
        string="Employee",
        ondelete='cascade',
    )
    contract_type_id = fields.Many2one(
        comodel_name='contract.type',
        string="Loại hợp đồng",
        ondelete='set null',
    )
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('running', 'Đang chạy'),
        ('expired', 'Hết hạn'),
        ('terminated', 'Đã chấm dứt'),
    ], string="Trạng thái", default='draft')
    salary = fields.Float(string="Lương")
    allowance_ids = fields.One2many(
        comodel_name='contract.allowance',
        inverse_name='contract_id',
        string="Phụ cấp",
    )
    salary_history_ids = fields.One2many(
        comodel_name='contract.salary.history',
        inverse_name='contract_id',
        string="Lịch sử lương",
    )
    total_salary = fields.Float(
        string="Tổng lương",
        compute='_compute_total_salary',
        store=True,
    )

    @api.depends('salary', 'allowance_ids.amount')
    def _compute_total_salary(self):
        for rec in self:
            rec.total_salary = rec.salary + sum(rec.allowance_ids.mapped('amount'))

    def _log_salary_history(self):
        """Tạo 1 bản ghi lịch sử lương, snapshot lại đúng start_date/end_date/salary
        hiện tại của hợp đồng."""
        for rec in self:
            self.env['contract.salary.history'].create({
                'contract_id': rec.id,
                'salary': rec.salary,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
            })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._log_salary_history()
        return records

    def action_confirm(self):
        self.write({'state': 'running'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_terminate(self):
        self.write({'state': 'terminated'})

    def _cron_expire_contracts(self):
        """Chạy định kỳ (ir.cron): tự động chuyển các hợp đồng 'Đang chạy'
        đã quá end_date sang trạng thái 'Hết hạn'."""
        today = fields.Date.today()
        expired_contracts = self.search([
            ('state', '=', 'running'),
            ('end_date', '<', today),
        ])
        if expired_contracts:
            expired_contracts.write({'state': 'expired'})

    def write(self, vals):
        result = super().write(vals)
        self._log_salary_history()
        return result

    @api.onchange('contract_type_id', 'start_date')
    def _onchange_contract_type_id(self):
        if self.contract_type_id and self.start_date:
            self.end_date = self.start_date + relativedelta(
                months=self.contract_type_id.default_duration
            )

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date >= rec.end_date:
                raise ValidationError(
                    "Ngày bắt đầu (%s) phải nhỏ hơn ngày kết thúc (%s)! "
                    "Vui lòng kiểm tra lại." % (rec.start_date, rec.end_date)
                )

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            if rec.code:
                if len(rec.code) > 20:
                    raise ValidationError(
                        "Mã hợp đồng không được quá 20 ký tự!"
                    )
                duplicate = self.search([
                    ('code', '=', rec.code),
                    ('id', '!=', rec.id),
                ])
                if duplicate:
                    raise ValidationError(
                        "Mã hợp đồng '%s' đã tồn tại, vui lòng nhập mã khác!" % rec.code
                    )

    @api.constrains('employee_id', 'state')
    def _check_one_running_contract(self):
        for rec in self:
            if rec.employee_id and rec.state == 'running':
                duplicate = self.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'running'),
                    ('id', '!=', rec.id),
                ])
                if duplicate:
                    raise ValidationError(
                        "Nhân viên '%s' đã có 1 hợp đồng đang chạy, "
                        "không thể có 2 hợp đồng cùng ở trạng thái 'Đang chạy'!"
                        % rec.employee_id.name
                    )