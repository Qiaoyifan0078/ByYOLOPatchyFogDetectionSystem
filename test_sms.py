# test_sms.py
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from sms_service import sms_service

print("=" * 60)
print("团雾预警短信发送测试")
print("=" * 60)
print()

# 配置信息
print("当前配置:")
print(f"服务商: {sms_service.provider}")
print(f"账号: {sms_service.ihuyi_account}")
print(f"密码: {'*' * len(sms_service.ihuyi_password)}")
print(f"签名: {sms_service.sign_name}")
print()

# 显示预期的短信格式
print("预期短信格式:")
print("【团雾预警系统】警告！{路段}路段出现{团雾等级}，能见度{能见度}，请立即减速至{限速}。注意行车安全！")
print()

# 测试发送
test_phone = input("请输入测试手机号 : ").strip()
if not test_phone:
    test_phone = "18035855929"

print(f"\n开始发送测试短信到: {test_phone}")
print("-" * 50)

result = sms_service.send_sms(
    phone=test_phone,
    road_section="G15沈海高速K100+500",
    fog_level="中度团雾",
    visibility="200-500米",
    speed_limit="60km/h"
)

print("\n发送结果:")
print(f"成功: {result['success']}")
print(f"消息: {result['message']}")
print(f"业务ID: {result['biz_id']}")
print("=" * 60)

if result['success']:
    print("✅ 短信发送成功！请检查手机是否收到团雾预警短信。")
else:
    print(f"❌ 发送失败: {result['message']}")
