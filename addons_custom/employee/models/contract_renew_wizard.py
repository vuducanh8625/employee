from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ContractRenewWizard(models.TransientModel):
    _name = 'contract.renew.wizard'
    _description = 'Wizard gia hạn hợp đồng'

    contract_id = fields.Many2one(
        comodel_name='contract',
        string="Hợp đồng cũ",
        required=True,
    )
    new_start_date = fields.Date(string="Ngày bắt đầu mới", required=True)
    new_end_date = fields.Date(string="Ngày kết thúc mới", required=True)
    new_salary = fields.Float(string="Lương mới")

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            self.new_salary = self.contract_id.salary
            if self.contract_id.end_date:
                self.new_start_date = self.contract_id.end_date + relativedelta(days=1)
                if self.contract_id.contract_type_id:
                    self.new_end_date = self.new_start_date + relativedelta(
                        months=self.contract_id.contract_type_id.default_duration
                    )

    def _get_renewal_code(self, old_code):
        """Sinh mã hợp đồng mới dựa trên mã cũ, tránh trùng khi gia hạn nhiều lần.

        Quy tắc: <mã_gốc>-R<n>
        Ví dụ: HD001 -> HD001-R1 -> HD001-R2 -> ...
        """
        base_code = old_code.split('-R')[0] if old_code else old_code

        Contract = self.env['contract']
        n = 1
        new_code = f"{base_code}-R{n}"
        # Tăng dần số hậu tố đến khi tìm được mã chưa tồn tại
        while Contract.search_count([('code', '=', new_code)]):
            n += 1
            new_code = f"{base_code}-R{n}"
        return new_code

    def action_confirm_renew(self):
        self.ensure_one()
        old = self.contract_id

        # Đóng hợp đồng cũ
        old.write({'state': 'expired'})

        # Tạo hợp đồng mới, nối tiếp (mã hợp đồng mới dựa trên mã cũ, không trùng)
        new_contract = self.env['contract'].create({
            'code': self._get_renewal_code(old.code),
            'name': old.name,
            'employee_id': old.employee_id.id,
            'contract_type_id': old.contract_type_id.id,
            'start_date': self.new_start_date,
            'end_date': self.new_end_date,
            'salary': self.new_salary,
            'state': 'running',
        })

        return {
            'name': "Hợp đồng mới",
            'type': 'ir.actions.act_window',
            'res_model': 'contract',
            'view_mode': 'form',
            'res_id': new_contract.id,
            'target': 'current',
        }