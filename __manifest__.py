# -*- coding: utf-8 -*-
{
    'name': "Odoo Wechat Connector",

    'summary': """
        企业微信应用模块""",

    'description': """
        企业微信应用模块，支持移动端应用场景
        更多支持：
        18951631470
        zou.jason@qq.com
    """,

    'author': "Jason Zou",
    'website': "http://www.duodoo.tech/",

    'category': '中国化应用/企业微信接口',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/groups_security.xml',
        'security/ir.model.access.csv',
        'data/ewi_wechat_data.xml',
        # 企业微信组织人员
        'views/ewi_wechat_config.xml',
        'views/ewi_interface.xml',
        # 'views/ewi_hr_empoyee.xml',
        # 'views/ewi_hr_department.xml',
        # 企业微信审批流
        # 'views/wx_oa/wx_approval_views.xml',
        # 'views/wx_oa/wx_approval_record_views.xml',
        # 'views/wx_oa/wx_approval_obj_views.xml',
        # 'views/wx_oa/wechat_menu.xml',
        'views/enterprise_wechat_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
