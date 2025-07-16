import axios from 'axios';

// 创建 axios 实例
const service = axios.create({
  // 这里是后端接口的基础路径，你可以先留空或指向你的后端
  // 比如：baseURL: 'http://localhost:8080/api'
  // 我们在 vite.config.js 中配置了代理，所以这里可以用相对路径
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', 
  timeout: 10000 // 请求超时时间
});

// 响应拦截器 (可选，但推荐)
service.interceptors.response.use(
  response => {
    // 假设后端返回的数据结构是 { code: 200, data: ..., message: '...' }
    const res = response.data;

    // 这里可以根据你和后端约定的成功码来判断
    // 如果不是成功状态码，就抛出错误
    if (res.code !== 200 && res.code !== 0) { // 兼容 code 为 0 或 200 的情况
        console.error('API Error:', res.message || 'Error');
        // 可以返回一个被拒绝的 Promise
        return Promise.reject(new Error(res.message || 'Error'));
    } else {
        // 如果成功，则只返回响应体中的 data 部分
        return res.data;
    }
  },
  error => {
    console.error('Network Error:', error); 
    return Promise.reject(error);
  }
);

export default service;