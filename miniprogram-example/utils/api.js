// utils/api.js - API 请求封装

const BASE_URL = 'http://your-server-ip:5000'; // 替换为你的服务器地址

/**
 * 获取存储的 token
 */
function getToken() {
  return wx.getStorageSync('token') || '';
}

/**
 * 保存 token
 */
function setToken(token) {
  if (token) {
    wx.setStorageSync('token', token);
  } else {
    wx.removeStorageSync('token');
  }
}

/**
 * 通用请求方法
 */
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

/**
 * 文件上传
 */
function uploadFile(url, filePath) {
  return new Promise((resolve, reject) => {
    const token = getToken();
    
    wx.uploadFile({
      url: BASE_URL + url,
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': `Bearer ${token}`
      },
      formData: {},
      success: (res) => {
        try {
          const data = JSON.parse(res.data);
          if (data.message === 'success') {
            resolve(data.data || {});
          } else {
            reject(new Error(data.message || '上传失败'));
          }
        } catch (e) {
          reject(new Error('响应解析失败'));
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
}

module.exports = {
  BASE_URL,
  getToken,
  setToken,
  request,
  get: (url) => request(url, { method: 'GET' }),
  post: (url, data) => request(url, { method: 'POST', data }),
  put: (url, data) => request(url, { method: 'PUT', data }),
  delete: (url) => request(url, { method: 'DELETE' }),
  uploadFile
};
