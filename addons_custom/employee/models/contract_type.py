from odoo import fields, models
from odoo.exceptions import ValidationError


class ContractType(models.Model):
    _name = 'contract.type'
    _description = 'Loại hợp đồng'

    name = fields.Char(string="Tên loại hợp đồng", required=True)
    default_duration = fields.Integer(
        string="Thời hạn mặc định (tháng)",
        default=12,
        help="Số tháng mặc định để tự động đề xuất Ngày kết thúc khi tạo hợp đồng.",
    )
    code = fields.Char(
        string="Mã loại hợp đồng",
        size=10,
        help="Dùng làm tiền tố khi sinh mã hợp đồng tự động. "
             "Ví dụ: 'HD1Y' cho hợp đồng 1 năm.",
    )
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string="Sequence sinh mã HĐ",
        readonly=True,
        copy=False,
    )
    # Lưu "YYYYMM" của lần sinh mã gần nhất, để biết khi nào cần
    # reset số đếm về 1 (sang tháng mới) mà không cần loop qua hợp đồng.
    last_code_period = fields.Char(readonly=True, copy=False)

    def _create_code_sequence(self):
        """Tạo 1 ir.sequence riêng cho loại hợp đồng này (chỉ số đếm thuần,
        phần Mã loại + Năm + Tháng do Python ghép, không đưa vào prefix)."""
        self.ensure_one()
        sequence = self.env['ir.sequence'].sudo().create({
            'name': f"Sequence mã hợp đồng - {self.name or self.code}",
            'code': f"contract.code.type.{self.id}",
            'padding': 4,
            'number_increment': 1,
            'number_next': 1,
            'implementation': 'no_gap',
        })
        self.sequence_id = sequence.id
        return sequence

    def _get_period(self):
        today = fields.Date.context_today(self)
        return '%04d%02d' % (today.year, today.month)

    def peek_next_contract_code(self):
        """Xem trước mã hợp đồng SẼ được sinh, dùng để hiển thị preview
        ngay khi tạo mới hợp đồng (chưa lưu). KHÔNG làm tăng số đếm thật -
        chỉ đọc giá trị number_next hiện tại của sequence.
        """
        self.ensure_one()
        if not self.code:
            return False
        if not self.sequence_id:
            # Chưa từng sinh mã lần nào -> preview số đầu tiên
            seq_part = '1'.zfill(4)
        else:
            period = self._get_period()
            if self.last_code_period != period:
                seq_part = '1'.zfill(self.sequence_id.padding or 4)
            else:
                seq_part = str(self.sequence_id.sudo().number_next).zfill(
                    self.sequence_id.padding or 4
                )
        return f"{self.code}{self._get_period()}{seq_part}"

    def get_next_contract_code(self):
        """Sinh mã hợp đồng THẬT (có tăng số đếm), theo công thức:
        <Mã loại HĐ><Năm YYYY><Tháng MM><Số tự tăng padding 4>
        Ví dụ: HD1Y2026070001
        """
        self.ensure_one()
        if not self.code:
            raise ValidationError(
                "Loại hợp đồng '%s' chưa có Mã loại hợp đồng, vui lòng "
                "cấu hình mã trước khi tạo hợp đồng!" % (self.name or '')
            )
        if not self.sequence_id:
            self._create_code_sequence()

        period = self._get_period()

        # Sang tháng mới (hoặc lần sinh đầu tiên) -> reset số đếm về 1
        if self.last_code_period != period:
            self.sequence_id.sudo().write({'number_next': 1})
            self.last_code_period = period

        seq_part = self.sequence_id.next_by_id()
        return f"{self.code}{period}{seq_part}"