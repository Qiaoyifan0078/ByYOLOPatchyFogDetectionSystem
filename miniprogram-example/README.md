# 微信小程序示例代码

这是团雾预警系统的微信小程序前端示例代码。

## 目录结构

```
miniprogram-example/
├── app.js                      # 小程序入口文件
├── app.json                    # 小程序配置文件
├── pages/
│   └── login/                  # 登录页面
│       ├── login.js            # 登录逻辑
│       ├── login.wxml          # 登录页面结构
│       └── login.wxss          # 登录页面样式
└── utils/
    └── api.js                  # API 请求封装
```

## 快速开始

### 1. 后端准备

确保 Flask 后端已启动并配置好微信小程序参数：

```bash
# 在 .env 文件中配置
WECHAT_APPID=wxXXXXXXXXXXXXXXX
WECHAT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# 执行数据库迁移（如果是现有数据库）
python migrate_wechat.py

# 启动服务
python app.py
```

### 2. 创建小程序项目

1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 打开开发者工具，选择"导入项目"
3. 选择 `miniprogram-example` 目录
4. 填写 AppID（或使用测试号）
5. 点击"导入"

### 3. 配置服务器域名

在微信公众平台配置服务器域名：

- **request 合法域名**：`https://your-domain.com`
- **uploadFile 合法域名**：`https://your-domain.com`

> 开发阶段可以在开发者工具中勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"

### 4. 修改 API 地址

在 `utils/api.js` 中修改 `BASE_URL` 为你的服务器地址：

```javascript
const BASE_URL = 'http://your-server-ip:5000'; // 替换为实际地址
```

### 5. 运行和调试

1. 在开发者工具中点击"编译"
2. 测试登录功能
3. 测试图片识别功能
4. 测试预警发布功能

## 主要功能

### 微信登录

使用 `wx.login()` 获取 code，发送到后端换取 token：

```javascript
wx.login({
  success: (res) => {
    if (res.code) {
      api.post('/api/wechat/login', { code: res.code })
        .then((data) => {
          api.setToken(data.token);
          // 登录成功
        });
    }
  }
});
```

### 图片识别

使用 `wx.chooseMedia()` 选择图片，然后上传到后端：

```javascript
wx.chooseMedia({
  count: 1,
  mediaType: ['image'],
  success: (res) => {
    const filePath = res.tempFiles[0].tempFilePath;
    api.uploadFile('/api/detect/image', filePath)
      .then((result) => {
        // 识别成功
      });
  }
});
```

### 发布预警

调用后端 API 发布预警信息：

```javascript
api.post('/api/warnings', {
  detection_id: result.id,
  source_type: 'image',
  road_section: 'G15沈海高速K100+500',
  fog_level: '中度团雾',
  visibility_level: '200-500米',
  speed_limit: '60km/h',
  snapshot_url: result.output_url
});
```

## API 接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/wechat/login` | POST | 微信登录 |
| `/api/wechat/bind-phone` | POST | 绑定手机号 |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/detect/image` | POST | 图片识别 |
| `/api/detect/video` | POST | 视频识别 |
| `/api/warnings` | POST | 发布预警 |
| `/api/warnings` | GET | 获取预警列表 |

## 注意事项

1. **HTTPS 要求**：生产环境必须使用 HTTPS
2. **Token 管理**：Token 有效期为 12 小时，需要实现自动刷新
3. **图片大小限制**：后端限制最大 600MB，建议小程序端压缩图片
4. **短信通知**：用户需绑定手机号才能接收预警短信

## 完整文档

详细的使用指南请参考：[WECHAT_MINIPROGRAM_GUIDE.md](../WECHAT_MINIPROGRAM_GUIDE.md)

## 技术支持

如有问题，请查看：
- 微信小程序官方文档：https://developers.weixin.qq.com/miniprogram/dev/framework/
- Flask 后端日志：`logs/flask.out.log`
