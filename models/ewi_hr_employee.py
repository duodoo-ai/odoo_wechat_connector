# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/22 08:44
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import models, fields


class StaffEMPAccount(models.Model):
    _inherit = 'staff'

    ewc_enable = fields.Boolean(string='禁用企业微信', default=False, help='企微：勾选表示禁用成员，默认不勾选')
