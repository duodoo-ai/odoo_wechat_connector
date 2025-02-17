# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/22 08:44
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import models, fields, exceptions
import os
import json
import logging
import requests
_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
headers = {'content-type': 'application/json'}


class EwiWechatConfig(models.Model):
    _name = 'ewi.wechat.config'
    _description = '企业微信接口'

    # 定义接口基本信息
    name = fields.Char(string='Auth接口名称', default='获取企业微信接口调用token', help='API名称')
    token_url = fields.Char(string='通讯录TokenUrl',
                            default='https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&amp;corpsecret={}',
                            help='token_url')
    corp_id = fields.Char(string='企业ID',
                          default='ww5a789309ca91ec7e',
                          help='路径：我的企业-企业信息-企业ID')
    corp_secret = fields.Char(string='通讯录Secret',
                              default='njqm0RDRzZAdNeSGqUpuAAm909LxdDQjIzPB1RzMKuU',
                              help='路径：管理工具-通讯录同步-Secret-查看')
    access_token = fields.Text(string='通讯录Token', help='通过token_url，corp_id，corp_secret，请求返回')
    department_id = fields.Char(string='公司部门id', default=1)
    msg = fields.Char(string='接口请求结果', help='返回code，成功success ')

    # 定义“审批”应用对接信息
    sp_AgentId = fields.Char(string='审批AgentId',
                             default='3010040',
                             help='路径：审批-AgentId')
    sp_Secret = fields.Char(string='审批Secret',
                            default='ub3ELV5X9d1JGkwmC9If_qr0szG78ogYBnGKZnCQPEg',
                            help='路径：审批-Secret-查看')
    sp_URL = fields.Char(string='审批URL',
                         default='http://bpm-test.dingyang.com:8069/corp_handler',
                         help='路径：审批-接收消息服务器配置-URL')
    sp_access_token = fields.Char(string='审批Token',
                                  default='TKkL0wVvklvIXD',
                                  help='路径：审批-接收消息服务器配置-Token')
    sp_EncodingAESKey = fields.Char(string='审批EncodingAESKey',
                                    default='vzpWA1cL9D8vPwgFOqTjFaysLhNbV36kWcXODL6knxf',
                                    help='路径：审批-接收消息服务器配置-EncodingAESKey')

    def action_token_from_wechat(self):
        # ===========================Token===============================
        # Step1：配置host地址、端口号、appKey和appSecret
        # api config
        # phoenix = self.env['ewi.wechat.config'].search([('name', '=', '获取企业微信接口调用token')])
        # url_token = '{}'.format(phoenix.url + ':' + phoenix.port + '/token')
        pass