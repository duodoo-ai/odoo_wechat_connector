# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/22 08:44
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import models, fields, api


class StaffDeptManage(models.Model):
    _inherit = 'hr.department'

    ewc_dept_order = fields.Integer('企微部门order', store=True)

    # @api.depends('depart_code', 'name', 'parent_id', 'dtype')
    # def _compute_ewc_dept_order(self):
    #     """计算企业微信部门排序号"""
    #     for order in self:
    #         order.update({'ewc_dept_order': -(int(order.depart_code) - 9999999)})
