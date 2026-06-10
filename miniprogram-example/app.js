// 微信小程序快速开始示例
// 将此代码复制到您的微信小程序项目中

// app.js
App({
  onLaunch() {
    // 检查登录状态
    this.checkLogin();
  },
  
  globalData: {
    userInfo: null,
    token: null
  },
  
  checkLogin() {
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.token = token;
      // 验证 token 有效性
      this.validateToken();
    }
  },
  
  validateToken() {
    wx.request({
      url: 'http://your-server-ip:5000/api/auth/me',
      header: {
        'Authorization': `Bearer ${this.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.globalData.userInfo = res.data.data.user;
        } else {
          // Token 失效，清除
          wx.removeStorageSync('token');
          this.globalData.token = null;
        }
      }
    });
  }
});
