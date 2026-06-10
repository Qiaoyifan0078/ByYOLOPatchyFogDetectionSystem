# 微信小程序接入指南

## 概述

本系统已支持微信小程序接入，提供以下功能：
- 微信一键登录
- 手机号绑定
- 团雾识别检测
- 预警信息发布
- 短信验证码通知

## 后端配置

### 1. 数据库迁移

如果数据库已经存在，需要添加 `wechat_openid` 字段：

```sql
ALTER TABLE users ADD COLUMN wechat_openid VARCHAR(128) DEFAULT NULL;
ALTER TABLE users ADD INDEX idx_wechat_openid (wechat_openid);
```

或者重新初始化数据库：

```bash
python init_db.py
```

### 2. 配置微信小程序参数

在 `.env` 文件中配置微信小程序的 AppID 和 Secret：

```env
# 微信小程序配置
WECHAT_APPID=wxXXXXXXXXXXXXXXX
WECHAT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**获取方式：**
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入小程序管理后台
3. 开发 -> 开发管理 -> 开发设置
4. 复制 AppID 和 AppSecret

### 3. 启动服务

```bash
python app.py
```

微信小程序 API 接口地址：
- 登录：`POST /api/wechat/login`
- 绑定手机：`POST /api/wechat/bind-phone`
- 获取配置：`GET /api/wechat/config`

## 微信小程序前端开发

### 1. 项目结构建议

```
miniprogram/
├── pages/
│   ├── index/          # 首页
│   ├── login/          # 登录页
│   ├── detect/         # 识别页
│   └── warnings/       # 预警列表
├── components/         # 组件
├── utils/
│   └── api.js         # API 请求封装
├── app.js
└── app.json
```

### 2. API 请求封装 (utils/api.js)

```javascript
const BASE_URL = 'http://your-server-ip:5000'; // 替换为你的服务器地址

function getToken() {
  return wx.getStorageSync('token') || '';
}

function setToken(token) {
  if (token) {
    wx.setStorageSync('token', token);
  } else {
    wx.removeStorageSync('token');
  }
}

function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    const token = getToken();
    const header = {
      'Content-Type': 'application/json',
      ...options.header
    };
    
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }
    
    wx.request({
      url: BASE_URL + url,
      method: options.method || 'GET',
      data: options.data || {},
      header: header,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data.data || {});
        } else {
          reject(new Error(res.data.message || '请求失败'));
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
}

module.exports = {
  getToken,
  setToken,
  request,
  get: (url) => request(url, { method: 'GET' }),
  post: (url, data) => request(url, { method: 'POST', data }),
  upload: (url, filePath) => {
    return new Promise((resolve, reject) => {
      const token = getToken();
      wx.uploadFile({
        url: BASE_URL + url,
        filePath: filePath,
        name: 'file',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          const data = JSON.parse(res.data);
          if (data.message === 'success') {
            resolve(data.data || {});
          } else {
            reject(new Error(data.message || '上传失败'));
          }
        },
        fail: reject
      });
    });
  }
};
```

### 3. 微信登录实现 (pages/login/login.js)

```javascript
const api = require('../../utils/api');

Page({
  data: {
    loading: false
  },

  onLoad() {
    this.checkLogin();
  },

  checkLogin() {
    const token = api.getToken();
    if (token) {
      // 验证 token 是否有效
      api.get('/api/auth/me')
        .then(() => {
          wx.switchTab({ url: '/pages/index/index' });
        })
        .catch(() => {
          api.setToken('');
        });
    }
  },

  handleLogin() {
    this.setData({ loading: true });
    
    wx.login({
      success: (res) => {
        if (res.code) {
          // 发送 res.code 到后台换取 openid
          api.post('/api/wechat/login', { code: res.code })
            .then((data) => {
              api.setToken(data.token);
              wx.showToast({ title: '登录成功', icon: 'success' });
              
              setTimeout(() => {
                wx.switchTab({ url: '/pages/index/index' });
              }, 1500);
            })
            .catch((err) => {
              wx.showToast({ title: err.message || '登录失败', icon: 'none' });
            })
            .finally(() => {
              this.setData({ loading: false });
            });
        } else {
          wx.showToast({ title: '登录失败', icon: 'none' });
          this.setData({ loading: false });
        }
      },
      fail: () => {
        wx.showToast({ title: '登录失败', icon: 'none' });
        this.setData({ loading: false });
      }
    });
  },

  handleGetPhoneNumber(e) {
    if (e.detail.errMsg === 'getPhoneNumber:ok') {
      // 这里需要解密手机号，建议使用云开发或后端解密
      wx.showToast({ title: '手机号获取成功', icon: 'success' });
    }
  }
});
```

### 4. 图片识别示例 (pages/detect/detect.js)

```javascript
const api = require('../../utils/api');

Page({
  data: {
    imageUrl: '',
    result: null,
    loading: false
  },

  chooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        this.setData({ imageUrl: tempFilePath });
        this.uploadAndDetect(tempFilePath);
      }
    });
  },

  uploadAndDetect(filePath) {
    this.setData({ loading: true });
    
    api.upload('/api/detect/image', filePath)
      .then((result) => {
        this.setData({ result });
        wx.showToast({ title: '识别成功', icon: 'success' });
      })
      .catch((err) => {
        wx.showToast({ title: err.message || '识别失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  publishWarning() {
    if (!this.data.result) {
      wx.showToast({ title: '请先进行识别', icon: 'none' });
      return;
    }

    wx.showModal({
      title: '发布预警',
      content: '确认发布团雾预警信息？',
      success: (res) => {
        if (res.confirm) {
          api.post('/api/warnings', {
            detection_id: this.data.result.id,
            source_type: 'image',
            road_section: 'G15沈海高速K100+500',
            fog_level: '中度团雾',
            visibility_level: '200-500米',
            speed_limit: '60km/h',
            snapshot_url: this.data.result.output_url
          })
          .then(() => {
            wx.showToast({ title: '预警发布成功', icon: 'success' });
          })
          .catch((err) => {
            wx.showToast({ title: err.message || '发布失败', icon: 'none' });
          });
        }
      }
    });
  }
});
```

### 5. 页面配置示例 (app.json)

```json
{
  "pages": [
    "pages/login/login",
    "pages/index/index",
    "pages/detect/detect",
    "pages/warnings/warnings"
  ],
  "window": {
    "navigationBarTitleText": "团雾预警系统",
    "navigationBarBackgroundColor": "#0f766e",
    "navigationBarTextStyle": "white"
  },
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#0f766e",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页"
      },
      {
        "pagePath": "pages/detect/detect",
        "text": "识别"
      },
      {
        "pagePath": "pages/warnings/warnings",
        "text": "预警"
      }
    ]
  }
}
```

## API 接口说明

### 1. 微信登录

**接口：** `POST /api/wechat/login`

**请求参数：**
```json
{
  "code": "微信登录凭证"
}
```

**返回数据：**
```json
{
  "token": "JWT Token",
  "user": {
    "id": 1,
    "username": "wx_abc12345",
    "full_name": "微信用户abc123",
    "role": "user"
  }
}
```

### 2. 绑定手机号

**接口：** `POST /api/wechat/bind-phone`

**请求头：**
```
Authorization: Bearer {token}
```

**请求参数：**
```json
{
  "phone": "13800138000"
}
```

**返回数据：**
```json
{
  "message": "绑定成功"
}
```

### 3. 图片识别

**接口：** `POST /api/detect/image`

**请求头：**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**请求参数：**
- file: 图片文件

**返回数据：**
```json
{
  "id": 1,
  "count": 3,
  "confidence_avg": 0.85,
  "confidence_max": 0.92,
  "output_url": "/outputs/xxx.jpg",
  "items": [...]
}
```

### 4. 发布预警

**接口：** `POST /api/warnings`

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**请求参数：**
```json
{
  "detection_id": 1,
  "source_type": "image",
  "road_section": "G15沈海高速K100+500",
  "fog_level": "中度团雾",
  "visibility_level": "200-500米",
  "speed_limit": "60km/h",
  "snapshot_url": "/outputs/xxx.jpg"
}
```

**返回数据：**
```json
{
  "item": {
    "id": 1,
    "road_section": "G15沈海高速K100+500",
    "fog_level": "中度团雾",
    ...
  }
}
```

## 注意事项

1. **服务器域名配置**
   - 在微信小程序后台配置 request 合法域名
   - 配置 uploadFile 合法域名
   - 开发阶段可以在开发者工具中勾选"不校验合法域名"

2. **HTTPS 要求**
   - 生产环境必须使用 HTTPS
   - 可以使用 Nginx 反向代理或使用云服务

3. **短信通知**
   - 用户绑定手机号后，发布预警时会自动发送短信
   - 短信格式：`您的验证码是：{预警信息}。请不要把验证码泄露给其他人。`

4. **安全性**
   - Token 有效期为 12 小时
   - 建议在小程序端实现 Token 自动刷新机制
   - 敏感操作需要二次确认

## 测试流程

1. 配置好 `.env` 中的微信小程序参数
2. 重启 Flask 服务
3. 在微信开发者工具中导入小程序项目
4. 测试登录、识别、预警发布等功能
5. 检查短信是否正常发送

## 常见问题

**Q: 微信登录失败？**
A: 检查 WECHAT_APPID 和 WECHAT_SECRET 是否正确配置，确保小程序已发布或添加了测试账号。

**Q: 无法上传图片？**
A: 检查服务器域名配置，确保 uploadFile 域名已添加到白名单。

**Q: 短信没有收到？**
A: 检查用户是否绑定了手机号，检查短信服务商配置是否正确。

## 技术支持

如有问题，请查看：
- Flask 日志：`logs/flask.out.log` 和 `logs/flask.err.log`
- 微信小程序控制台日志
- 数据库记录：`sms_logs` 表查看短信发送状态
