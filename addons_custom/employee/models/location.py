import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)

API_BASE_URL = 'https://provinces.open-api.vn/api/v2'


class Province(models.Model):
    _name = 'province'

    active = fields.Boolean(default=True)
    name = fields.Char(string="Tên tỉnh/thành phố")
    code = fields.Integer(string="Mã tỉnh")
    ward_ids = fields.One2many(
        comodel_name='ward',
        inverse_name='province_id',
        string="Xã/Phường",
    )

    def action_import_provinces_wards_from_api(self):
        """Đồng bộ dữ liệu Tỉnh/Phường từ provinces.open-api.vn (API v2).

        Cách chạy (không cần sửa file nào khác):
        1. Mở terminal, cd vào thư mục chứa odoo-bin
        2. Chạy: python odoo-bin shell -d ten_database_cua_ban
        3. Trong shell gõ:
               env['province'].action_import_provinces_wards_from_api()
               env.cr.commit()

        Có thể gọi lại bất cứ lúc nào để đồng bộ lại dữ liệu (idempotent:
        record đã có theo `code` sẽ được update thay vì tạo trùng).
        """
        Ward = self.env['ward']

        # 1. Lấy danh sách tỉnh/thành phố
        try:
            resp = requests.get(f'{API_BASE_URL}/p/', timeout=30)
            resp.raise_for_status()
            provinces_data = resp.json()
        except requests.RequestException as e:
            _logger.error("Không lấy được danh sách tỉnh từ API: %s", e)
            raise

        province_by_code = {}
        for p in provinces_data:
            province = self.search([('code', '=', p['code'])], limit=1)
            vals = {'name': p['name'], 'code': p['code']}
            if province:
                province.write(vals)
            else:
                province = self.create(vals)
            province_by_code[p['code']] = province

        # 2. Lấy danh sách xã/phường
        try:
            resp = requests.get(f'{API_BASE_URL}/w/', timeout=60)
            resp.raise_for_status()
            wards_data = resp.json()
        except requests.RequestException as e:
            _logger.error("Không lấy được danh sách phường/xã từ API: %s", e)
            raise

        ward_count = 0
        for w in wards_data:
            # LƯU Ý: kiểm tra lại tên field thực tế trong JSON trả về
            # (ví dụ 'province_code' hoặc tên khác) và chỉnh lại nếu cần.
            province = province_by_code.get(w.get('province_code'))
            if not province:
                continue
            vals = {
                'name': w['name'],
                'code': w['code'],
                'province_id': province.id,
            }
            ward = Ward.search([('code', '=', w['code'])], limit=1)
            if ward:
                ward.write(vals)
            else:
                Ward.create(vals)
            ward_count += 1

        _logger.info(
            "Đã đồng bộ %s tỉnh và %s phường/xã từ API",
            len(province_by_code), ward_count,
        )
        return True


class Ward(models.Model):
    _name = 'ward'

    active = fields.Boolean(default=True)
    name = fields.Char(string="Tên xã/phường")
    code = fields.Integer(string="Mã xã/phường")
    province_id = fields.Many2one(
        comodel_name='province',
        string="Tỉnh/Thành phố",
        ondelete='cascade',
    )