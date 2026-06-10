// pages/login/login.js - 微信登录页面

const api = require('../../utils/api');

Page({
  data: {
    loading: false,
    hasUserInfo: false
  },

  onLoad() {
    this.checkLoginStatus();
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = api.getToken();
    if (token) {
      // 验证 token 是否有效
      api.get('/api/auth/me')
        .then((data) => {
          wx.switchTab({ url: '/pages/index/index' });
        })
        .catch(() => {
          // Token 失效，清除
          api.setToken('');
        });
    }
  },

  /**
   * 微信一键登录
   */
  handleWechatLogin() {
    this.setData({ loading: true });
    
    wx.login({
      success: (res) => {
        if (res.code) {
          // 发送 code 到后端换取 openid 和 token
          api.post('/api/wechat/login', { code: res.code })
            .then((data) => {
              // 保存 token
              api.setToken(data.token);
              
              wx.showToast({ 
                title: '登录成功', 
                icon: 'success',
                duration: 1500
              });
              
              // 跳转到首页
              setTimeout(() => {
                wx.switchTab({ url: '/pages/index/index' });
              }, 1500);
            })
            .catch((err) => {
              wx.showToast({ 
                title: err.message || '登录失败', 
                icon: 'none' 
              });
            })
            .finally(() => {
              this.setData({ loading: false });
            });
        } else {
          wx.showToast({ title: '获取登录凭证失败', icon: 'none' });
          this.setData({ loading: false });
        }
      },
      fail: () => {
        wx.showToast({ title: '登录失败', icon: 'none' });
        this.setData({ loading: false });
      }
    });
  },

  /**
   * 获取手机号（可选）
   */
  handleGetPhoneNumber(e) {
    if (e.detail.errMsg === 'getPhoneNumber:ok') {
      // 这里需要后端解密手机号
      // 建议使用云开发或后端接口解密
      wx.showToast({ 
        title: '请使用绑定手机号功能', 
        icon: 'none' 
      });
    } else {
      wx.showToast({ 
        title: '用户拒绝授权', 
        icon: 'none' 
      });
    }
  }
});
