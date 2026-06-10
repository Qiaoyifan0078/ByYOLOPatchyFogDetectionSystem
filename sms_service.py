"""
短信发送服务模块
支持互亿无线、阿里云、腾讯云等短信服务商
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


logger = logging.getLogger(__name__)


class SMSService:
    """短信服务类"""

    def __init__(self):
        self.provider = os.getenv("SMS_PROVIDER", "ihuyi")

        # 互亿无线配置
        self.ihuyi_account = os.getenv("IHUYI_ACCOUNT", "")
        self.ihuyi_password = os.getenv("IHUYI_PASSWORD", "")
        self.ihuyi_url = os.getenv("IHUYI_URL", "https://api.ihuyi.com/sms/Submit.json")

        # 阿里云配置
        self.access_key_id = os.getenv("SMS_ACCESS_KEY_ID", "")
        self.access_key_secret = os.getenv("SMS_ACCESS_KEY_SECRET", "")
        self.sign_name = os.getenv("SMS_SIGN_NAME", "团雾预警系统")
        self.template_code = os.getenv("SMS_TEMPLATE_CODE", "")
        self.app_id = os.getenv("SMS_APP_ID", "")

    def send_sms(self, phone: str, road_section: str, fog_level: str,
                 visibility: str, speed_limit: str) -> dict:
        """
        发送预警短信

        Args:
            phone: 手机号
            road_section: 路段
            fog_level: 团雾等级
            visibility: 能见度
            speed_limit: 限速信息

        Returns:
            dict: {'success': bool, 'message': str, 'biz_id': str}
        """
        if not phone or len(phone) < 11:
            return {
                'success': False,
                'message': '手机号格式不正确',
                'biz_id': ''
            }

        # 构造团雾预警格式的短信内容（4个变量）
        content = f"【{self.sign_name}】警告！{road_section}路段出现{fog_level}，能见度{visibility}，请立即减速至{speed_limit}。注意行车安全！"

        try:
            if self.provider == "ihuyi":
                result = self._send_via_ihuyi(phone, content)
            elif self.provider == "aliyun":
                result = self._send_via_aliyun(phone, fog_level, road_section, visibility, speed_limit)
            elif self.provider == "tencent":
                result = self._send_via_tencent(phone, fog_level, road_section, visibility, speed_limit)
            else:
                result = self._send_mock(phone, content)

            logger.info(f"短信发送结果: phone={phone}, success={result['success']}, message={result['message']}")
            return result

        except Exception as e:
            logger.error(f"短信发送异常: {str(e)}")
            return {
                'success': False,
                'message': f'发送失败: {str(e)}',
                'biz_id': ''
            }

    def _send_via_ihuyi(self, phone: str, content: str) -> dict:
        """通过互亿无线发送短信"""
        try:
            if not self.ihuyi_account or not self.ihuyi_password:
                logger.warning("互亿无线账号或密码未配置，使用模拟模式")
                return self._send_mock(phone, content)

            # 互亿无线 API 参数（根据官方文档）
            payload = {
                'account': self.ihuyi_account,
                'password': self.ihuyi_password,
                'mobile': phone,
                'content': content,
                'format': 'json'
            }

            # 设置请求头
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            logger.info(f"发送短信: phone={phone}, account={self.ihuyi_account}")
            logger.info(f"请求URL: {self.ihuyi_url}")

            # 发送 POST 请求
            response = requests.post(
                self.ihuyi_url,
                data=payload,
                headers=headers,
                timeout=10
            )

            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text[:500]}")

            # 尝试解析 JSON
            try:
                result = response.json()
            except Exception as json_error:
                logger.error(f"JSON解析失败: {json_error}")
                logger.error(f"响应内容: {response.text}")
                return {
                    'success': False,
                    'message': f'API返回格式错误: {response.text[:200]}',
                    'biz_id': ''
                }

            # 互亿无线返回码判断：code=2 表示成功
            if result.get('code') == 2:
                return {
                    'success': True,
                    'message': '发送成功',
                    'biz_id': result.get('msgid', '')
                }
            else:
                error_msg = result.get('msg', '发送失败')
                return {
                    'success': False,
                    'message': f'互亿无线错误: {error_msg}',
                    'biz_id': ''
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"互亿无线请求失败: {str(e)}")
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}',
                'biz_id': ''
            }
        except Exception as e:
            logger.error(f"互亿无线发送失败: {str(e)}")
            return {
                'success': False,
                'message': f'互亿无线发送失败: {str(e)}',
                'biz_id': ''
            }

    def _send_via_aliyun(self, phone: str, fog_level: str, road_section: str,
                         visibility: str, speed_limit: str) -> dict:
        """通过阿里云发送短信"""
        try:
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkcore.request import CommonRequest

            client = AcsClient(
                self.access_key_id,
                self.access_key_secret,
                "cn-hangzhou"
            )

            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('dysmsapi.aliyuncs.com')
            request.set_method('POST')
            request.set_protocol_type('https')
            request.set_version('2017-05-25')
            request.set_action_name('SendSms')

            request.add_query_param('RegionId', "cn-hangzhou")
            request.add_query_param('PhoneNumbers', phone)
            request.add_query_param('SignName', self.sign_name)
            request.add_query_param('TemplateCode', self.template_code)

            template_param = {
                "road_section": road_section,
                "fog_level": fog_level,
                "visibility": visibility,
                "speed_limit": speed_limit
            }
            request.add_query_param('TemplateParam', json.dumps(template_param))

            response = client.do_action(request)
            result = json.loads(response)

            if result.get('Code') == 'OK':
                return {
                    'success': True,
                    'message': '发送成功',
                    'biz_id': result.get('BizId', '')
                }
            else:
                return {
                    'success': False,
                    'message': result.get('Message', '发送失败'),
                    'biz_id': ''
                }

        except ImportError:
            logger.warning("阿里云SDK未安装，使用模拟模式")
            content = f"【{self.sign_name}】团雾预警：{road_section}出现{fog_level}，能见度{visibility}，{speed_limit}。请注意行车安全！"
            return self._send_mock(phone, content)
        except Exception as e:
            logger.error(f"阿里云短信发送失败: {str(e)}")
            return {
                'success': False,
                'message': f'阿里云发送失败: {str(e)}',
                'biz_id': ''
            }

    def _send_via_tencent(self, phone: str, fog_level: str, road_section: str,
                          visibility: str, speed_limit: str) -> dict:
        """通过腾讯云发送短信"""
        try:
            from tencentcloud.common import credential
            from tencentcloud.sms.v20210111 import sms_client, models

            cred = credential.Credential(self.access_key_id, self.access_key_secret)
            client = sms_client.SmsClient(cred, "ap-guangzhou")

            req = models.SendSmsRequest()
            req.PhoneNumberSet = [f"+86{phone}"]
            req.SmsSdkAppId = self.app_id
            req.SignName = self.sign_name
            req.TemplateId = self.template_code
            req.TemplateParamSet = [road_section, fog_level, visibility, speed_limit]

            resp = client.SendSms(req)

            if resp.SendStatusSet and resp.SendStatusSet[0].Code == "Ok":
                return {
                    'success': True,
                    'message': '发送成功',
                    'biz_id': resp.SendStatusSet[0].SerialNo
                }
            else:
                return {
                    'success': False,
                    'message': resp.SendStatusSet[0].Message if resp.SendStatusSet else '发送失败',
                    'biz_id': ''
                }

        except ImportError:
            logger.warning("腾讯云SDK未安装，使用模拟模式")
            content = f"【{self.sign_name}】团雾预警：{road_section}出现{fog_level}，能见度{visibility}，{speed_limit}。请注意行车安全！"
            return self._send_mock(phone, content)
        except Exception as e:
            logger.error(f"腾讯云短信发送失败: {str(e)}")
            return {
                'success': False,
                'message': f'腾讯云发送失败: {str(e)}',
                'biz_id': ''
            }

    def _send_mock(self, phone: str, content: str) -> dict:
        """模拟发送短信（用于测试）"""
        logger.info(f"[模拟短信] 发送给 {phone}: {content}")
        return {
            'success': True,
            'message': '模拟发送成功',
            'biz_id': f'mock_{datetime.now().timestamp()}'
        }


sms_service = SMSService()

