# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'employee',
    'category': 'Human Resources',
    'summary': 'employyee',
    'version': '1.0',
    'depends': ['base','mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/employee.xml',
        'views/contract_type.xml',
        'views/employee_report.xml',
        'views/contract_renew_wizard.xml',
        'views/contract.xml',
        'views/menu.xml',
        'data/employee_sequence.xml',
        'data/employee_data.xml',
        'data/province_ward_cron.xml',
        'data/contract_expire_cron.xml',
    ],
    'installable': True,
    'auto_install': True,
    'author': '',
    'license': 'LGPL-3',
}