# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/23 08:44
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@ 一级部门/公司跳过不处理，需手动维护ODOO与企业微信一级部门名称一致
"""
from odoo import models, fields, exceptions
import os
import json
import logging
import requests
_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
headers = {'content-type': 'application/json'}


class EWIInterface(models.Model):
    _name = 'ewi.interface'
    _description = '企业微信接口'

    name = fields.Char(string='接口名称', required=True, tracking=True)
    description = fields.Char(string='接口说明', tracking=True)
    AgentId = fields.Char(string='应用AgentId', help='本项在应用对接的时候应填入')
    Secret = fields.Char(string='应用凭证密钥Secret', help='应用的凭证密钥，注意应用需要是启用状态，获取方式参考：术语说明-secret')
    url = fields.Text(string='TokenUrl')
    access_token = fields.Text(string='Token', help='获取到的凭证，最长为512字节，通过corp_id，Secret请求返回')
    errcode = fields.Char(string='errcode', help='出错返回码，为0表示成功，非0表示调用失败')
    errmsg = fields.Char(string='errmsg', help='返回码提示语')
    expires_in = fields.Char(string='expires_in', help='凭证的有效时间（秒）')

    def btn_execute(self):
        """
        按钮执行函数，可用于触发一系列操作
        """
        if self.name == '通讯录同步授权':
            self.gen_contacts_access_token()     # 获得连接Token，通讯录授权
        if self.name == 'R2':
            self.send_message()     # 发送各种应用消息
        # # 示例：调用部门相关接口
        if self.name == '创建部门':
            self.new_department()
        # self.update_department()
        # self.delete_department()
        # # 调用人员相关接口
        # self.gen_employee_userid_list()
        if self.name == '创建成员':
            self.new_employee()

    def gen_contacts_access_token(self):
        """授权信息，获取企微通讯录Access Token"""
        access_obj = self.env['ewi.wechat.config']
        access_record = access_obj.search([('name', '=', '企业微信接口')])
        corp_id = access_record.corp_id
        corp_secret = self.Secret
        if not corp_id or not corp_secret:
            _logger.info(f"通讯录授权信息{corp_id}----{corp_secret}为空，请填入！")
            return
        token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
        _logger.info(f"通讯录访问 Token_url -----  {token_url}")
        for line in self:
            try:
                ret = requests.get(token_url, headers=headers)
                ret.raise_for_status()
                result = ret.json()
                if result.get('errcode') == 0:
                    line.write({'access_token': result['access_token'],
                                         'errcode': result['errcode'],
                                         'errmsg': result['errmsg'],
                                         'expires_in': result['expires_in'],
                                         })
                    return result['access_token']
                else:
                    _logger.error(f"获取企微通讯录Access Token失败: {result.get('errmsg')}")
                    return None
            except requests.RequestException as e:
                _logger.error(f"请求获取企微通讯录Access Token时出错: {str(e)}")
                return None

    def gen_application_access_token(self):
        """授权信息，获取企微应用授权Access Token"""
        access_obj = self.env['ewi.wechat.config']
        access_record = access_obj.search([('name', '=', '企业微信接口')])
        corp_id = access_record.corp_id
        corp_secret = self.Secret       # 通过每个应用动态获得
        _logger.info(f"应用授权信息{corp_id} --- {corp_secret}")
        if not corp_id or not corp_secret:
            _logger.info(f"应用授权信息{corp_secret}为空，请填入！")
            return
        token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
        for line in self:
            try:
                ret = requests.get(token_url, headers=headers)
                ret.raise_for_status()
                result = ret.json()
                if result.get('errcode') == 0:
                    line.write({'access_token': result['access_token'],
                                         'errcode': result['errcode'],
                                         'errmsg': result['errmsg'],
                                         'expires_in': result['expires_in'],
                                         })
                    return result['access_token']
                else:
                    _logger.error(f"获取企业应用Access Token失败: {result.get('errmsg')}")
                    return None
            except requests.RequestException as e:
                _logger.error(f"获取企业应用Access Token时出错: {str(e)}")
                return None

    def send_message(self):
        """发送各种应用消息"""
        access_token = self.gen_application_access_token()
        if not access_token:
            _logger.info(f"创建应用消息-----access_token------凭证为空 {access_token}")
            return
        token_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        data = {
           "touser" : "18066043008",
           # "toparty" : "PartyID1|PartyID2",
           # "totag" : "TagID1 | TagID2",
           "msgtype" : "text",
           "agentid" : self.AgentId,
           "text" : {
               "content" : "你的快递已到，请携带工卡前往邮件中心领取。聪明避开排队。"
           },
           "safe":0,
           "enable_id_trans": 0,
           "enable_duplicate_check": 0,
           "duplicate_check_interval": 1800
        }
        ret = requests.post(token_url, data=json.dumps(data), headers=headers)
        if json.loads(ret.text)['errcode'] == 0:
            _logger.info("发送应用消息成功{}".format(json.loads(ret.text)))
        else:
            _logger.error("发送应用消息失败{}".format(json.loads(ret.text)))

    def new_department(self):
        """部门接口，创建部门"""
        access_token = self.gen_contacts_access_token()
        if not access_token:
            _logger.info(f"创建部门-----access_token------凭证为空 {access_token}")
            return
        # 去拿Odoo本地的组织架构
        depart_obj = self.with_user(2).env['hr.department']
        depart_records = depart_obj.search([])
        odoo_dept_list = [i['id'] for i in depart_records]  # odoo中正常使用的部门ID
        # 去请求企业微信组织架构
        search_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/department/simplelist?access_token={access_token}"
        response = requests.get(search_token_url, headers=headers)  # 请求企业微信正常使用的部门ID
        _logger.info(f"企业微信请求部门状态 ----【{response.status_code}】 ----")
        create_dept_list = []
        try:
            if response.status_code == 200:
                ret = json.loads(response.text)
                wechat_dept_list = [i['id'] for i in ret['department_id']]  # 企业微信正常使用的部门ID
                create_dept_list = [i for i in odoo_dept_list if i not in wechat_dept_list]  # 需要创建的部门ID
        except Exception as e:
            _logger.info(f"企业微信请求部门有误 ---- {e} ----")

        # 需要创建的部门ID
        create_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/department/create?access_token={access_token}"
        print(create_dept_list)
        for wid in create_dept_list:
            # 一级部门/公司跳过不处理，需手动维护ODOO与企业微信一级部门 名称一致
            depart_id = depart_obj.search([('id', '=', wid)])
            if not depart_id.parent_id.id:
                continue
            data = {
                "name": depart_id.name,
                "parentid": depart_id.parent_id.id or False,
                "id": depart_id.id,
                "order": depart_id.id,
            }
            ret = requests.post(create_token_url, data=json.dumps(data), headers=headers)
            if ret.status_code == 200:
                _logger.info("创建部门成功{}".format(json.loads(ret.text)))
            else:
                _logger.error("创建部门失败{}".format(json.loads(ret.text)))

    def update_department(self):
        """部门接口，企微部门更新"""
        token = self.gen_access_token()
        if not token:
            return
        update_depart_url = self.with_user(2).env['ewi.interface'].search([('name', '=', '更新部门')]).url

        depart_records = self.with_user(2).env['hr.department'].search([])  # 换部门上下级、换部门负责人、部门更名
        odoo_dept_list = [i['id'] for i in depart_records]  # odoo中正常使用的部门ID

        # odoo中正常使用的部门ID
        for i in odoo_dept_list:  # 全量更新企业微信数据
            record_id = self.with_user(2).env['hr.department'].search([('id', '=', i)])
            if i == 1:
                continue
            data = {
                "id": record_id.id,
                "name": record_id.name,  # 部门更名
                "parentid": record_id.parent_id.id or False,  # 换部门上下级
                "order": record_id.ewc_dept_order,
            }
            ret = requests.post(update_depart_url.format(token), data=json.dumps(data), headers=headers)
            if json.loads(ret.text)['errcode'] == 0:
                _logger.info("更新部门成功{}".format(json.loads(ret.text)))
            else:
                _logger.error("更新部门失败{}".format(json.loads(ret.text)))

    def delete_department(self):
        """部门接口，企微部门删除"""
        token = self.gen_access_token()
        if not token:
            return
        delete_depart_url = self.with_user(2).env['ewi.interface'].search([('name', '=', '删除部门')]).url

        depart_records_is_leaf = self.with_user(2).env['hr.department'] \
            .search([('active', '=', False), ('is_leaf', '=', True)])  # 取部门标识为归档的数据，层级为末级数据
        odoo_dept_list_is_leaf = [i['id'] for i in depart_records_is_leaf]  # odoo中已停用的部门ID

        depart_records_not_leaf = self.with_user(2).env['shr.department'] \
            .search([('active', '=', False), ('is_leaf', '=', False)])  # 取部门标识为归档的数据，层级为非末级数据
        odoo_dept_list_not_leaf = [i['id'] for i in depart_records_not_leaf]  # odoo中已停用的部门ID

        # odoo中已停止使用的部门ID
        for i in odoo_dept_list_is_leaf:  # 全取部门标识为归档的数据，层级为末级数据
            if i == 1:
                continue
            ret = requests.get(delete_depart_url.format(token, i), headers=headers)
            if json.loads(ret.text)['errcode'] == 0:
                _logger.info("删除部门成功{}".format(json.loads(ret.text)))
            else:
                _logger.error("删除部门失败{}".format(json.loads(ret.text)))

        # odoo中已停止使用的部门ID
        for i in odoo_dept_list_not_leaf:  # 全取部门标识为归档的数据，层级为非末级数据
            if i == 1:
                continue
            ret = requests.get(delete_depart_url.format(token, i), headers=headers)
            if json.loads(ret.text)['errcode'] == 0:
                _logger.info("删除部门成功{}".format(json.loads(ret.text)))
            else:
                _logger.error("删除部门失败{}".format(json.loads(ret.text)))

    def gen_employee_userid_list(self):
        """
        人员接口，获取部门成员ID列表
        """
        token = self.gen_access_token()
        if not token:
            return
        gen_employee_userid_url = self.with_user(2).env['ewi.interface'].search([('name', '=', '获取成员ID列表')]).url
        userid_args = {
            "limit": 100
        }
        try:
            ret = requests.post(gen_employee_userid_url.format(token), json=userid_args, headers=headers)
            if json.loads(ret.text)['errcode'] == 0:
                _logger.info("获取部门成员ID列表成功{}".format(json.loads(ret.text)))
            else:
                _logger.error("获取部门成员ID列表失败{}".format(json.loads(ret.text)))
        except Exception as e:
            _logger.error('企业微信获取部门成员ID列表时连接失败：' + str(e))
            return

    def new_employee(self):
        """
        人员接口，获取部门成员
        """
        access_token = self.gen_contacts_access_token()
        if not access_token:
            _logger.info(f"创建成员-----access_token------凭证为空 {access_token}")
            return
        # 去拿Odoo本地的内部职工
        employee_obj = self.with_user(2).env['hr.employee']
        employee_records = employee_obj.search([])
        odoo_employee_list = [i['mobile_phone'] for i in employee_records]  # odoo中在职人员ID，原则上要求职工号企业内唯一
        # 去请求企业微信部门职工
        search_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/user/list_id?access_token={access_token}"
        response = requests.get(search_token_url, headers=headers)  # 请求企业微信正常使用的部门ID
        _logger.info(f"企业微信请求职工状态 ----【{response.status_code}】 ----")
        create_employee_list = []
        try:
            if response.status_code == 200:
                ret = json.loads(response.text)
                wechat_employee_list = [i['userid'] for i in ret['dept_user']]  # 企业微信在职人员ID
                create_employee_list = [i for i in odoo_employee_list if i not in wechat_employee_list]  # 需要创建的在职人员ID
        except Exception as e:
            _logger.info(f"企业微信请求职工有误 ---- {e} ----")

        # 需要创建的职工ID
        create_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/user/create?access_token={access_token}"
        print(create_employee_list)
        for employee in create_employee_list:
            employee_id = employee_obj.search([('mobile_phone', '=', '18066043008')])
            print(employee_id)
            # """填充主部门"""
            # depart_list = [employee_record.department_id.id]
            # """判断是否部门负责人"""
            # if employee_record.department_id.manager_id.id == employee_record.id:
            #     is_leader_in_dept_list = [1]
            # else:
            #     is_leader_in_dept_list = [0]
            # """设置”成员所属部门id列表“、是否”部门负责人“"""
            # for depart in employee_record.department_ids:
            #     depart_list.append(depart.id)
            #     is_leader_in_dept_list.append(0)
            data = {
                "userid": '18066043008',  # 是, 成员UserID
                "name": employee_id.name,  # 是, 成员名称
                # "alias": employee_record.work_no,  # 是, 成员别名
                "mobile": employee_id.mobile_phone,  # 手机号码
                "department": [22],  # 成员所属部门id列表
                # "position": employee_record.job_id.name,  # 职务信息
                # "gender": 1 if employee_record.gender == 'male' else 2,  # 性别。1表示男性，2表示女性
                # "email": employee_record.work_email,  # 邮箱
                # "is_leader_in_dept": is_leader_in_dept_list,  # 1表示为部门负责人，0表示非部门负责人
                # "direct_leader": ["%s" % employee_record.parent_id.work_no],  # 直属上级UserID
                # "enable": 0 if employee_record.ewc_enable else 1,  # 启用/禁用成员。1表示启用成员，0表示禁用成员
                # "telephone": employee_record.work_phone or False,  # 座机
                # "address": self.env['res.company'].search([('id', '=', '1')]).street or False,  # 地址
                # "main_department": employee_record.department_id.id,  # 主部门
                # "to_invite": to_invite,  # 是否邀请该成员使用企业微信
            }
            # if employee_record.depart_code == '1' or not employee_record.parent_id.id or not employee_record.job_id.name:
            #     del employee_args['direct_leader']
            # if not employee_record.job_id.name:
            #     del employee_args['position']
            # if not employee_record.work_email:
            #     del employee_args['email']
            ret = requests.post(create_token_url, data=json.dumps(data), headers=headers)
            if ret.status_code == 200:
                _logger.info("创建职工成功{}".format(json.loads(ret.text)))
            else:
                _logger.error("创建职工失败{}".format(json.loads(ret.text)))