from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Contract(models.Model):
    _name = 'contract'
    _description = 'Hợp đồng'

    name = fields.Char(string="Contract Name")
    code = fields.Char(string="Mã hợp đồng", size=20, readonly=True, copy=False)
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

    @api.model
    def _get_default_code_sequence(self):
        """Sequence dùng chung khi hợp đồng CHƯA chọn Loại hợp đồng (hoặc
        loại đó chưa có Mã loại hợp đồng), dùng prefix cố định 'HD'."""
        Sequence = self.env['ir.sequence'].sudo()
        seq = Sequence.search([('code', '=', 'contract.code.default')], limit=1)
        if not seq:
            seq = Sequence.create({
                'name': "Sequence mã hợp đồng mặc định (chưa chọn loại HĐ)",
                'code': 'contract.code.default',
                'padding': 4,
                'number_increment': 1,
                'number_next': 1,
                'implementation': 'no_gap',
            })
        return seq

    @api.model
    def _get_default_code_last_period(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'contract.default_code_last_period', default=''
        )

    @api.model
    def _set_default_code_last_period(self, period):
        self.env['ir.config_parameter'].sudo().set_param(
            'contract.default_code_last_period', period
        )

    @api.model
    def _peek_code(self, contract_type_id=None):
        """Xem trước mã hợp đồng (KHÔNG tăng số đếm thật) để hiển thị ngay
        khi mở form 'Mới', trước khi Lưu."""
        period = '%04d%02d' % (fields.Date.context_today(self).year,
                                fields.Date.context_today(self).month)
        if contract_type_id:
            contract_type = self.env['contract.type'].browse(contract_type_id)
            if contract_type.exists() and contract_type.code:
                return contract_type.peek_next_contract_code()
        # Chưa chọn Loại hợp đồng (hoặc loại chưa có mã) -> preview theo sequence mặc định
        seq = self._get_default_code_sequence()
        if self._get_default_code_last_period() != period:
            seq_part = '1'.zfill(seq.padding or 4)
        else:
            seq_part = str(seq.sudo().number_next).zfill(seq.padding or 4)
        return f"HD{period}{seq_part}"

    @api.model
    def _generate_code(self, contract_type_id=None):
        """Sinh mã hợp đồng THẬT (có tăng số đếm), gọi trong create()."""
        if contract_type_id:
            contract_type = self.env['contract.type'].browse(contract_type_id)
            if contract_type.exists() and contract_type.code:
                return contract_type.get_next_contract_code()
        # Chưa chọn Loại hợp đồng (hoặc loại chưa có mã) -> dùng sequence mặc định
        seq = self._get_default_code_sequence()
        period = '%04d%02d' % (fields.Date.context_today(self).year,
                                fields.Date.context_today(self).month)
        if self._get_default_code_last_period() != period:
            seq.sudo().write({'number_next': 1})
            self._set_default_code_last_period(period)
        seq_part = seq.next_by_id()
        return f"HD{period}{seq_part}"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'code' in fields_list:
            res['code'] = self._peek_code(res.get('contract_type_id'))
        return res

    @api.onchange('contract_type_id')
    def _onchange_contract_type_id_code_preview(self):
        # Chỉ cập nhật preview cho bản ghi CHƯA lưu; hợp đồng đã lưu thì
        # mã đã chốt, không được đổi khi đổi loại hợp đồng sau này.
        if not isinstance(self.id, int):
            self.code = self._peek_code(self.contract_type_id.id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Mã hiển thị trước đó (nếu có) chỉ là preview -> luôn tính lại
            # mã THẬT tại đây để đảm bảo số đếm chỉ tăng đúng 1 lần lúc Lưu.
            vals['code'] = self._generate_code(vals.get('contract_type_id'))
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