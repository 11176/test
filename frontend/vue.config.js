module.exports = {
  devServer: {
    proxy: {
      // 关键修改点：匹配所有/api开头的请求
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'  // 保持路径不变
        },
        logLevel: 'debug',
        // 新增连接配置
        agent: require('http').globalAgent,
        onError(err) {
          console.error('代理错误:', err)
        }
      }
    },
    // 强制热更新配置
    hot: true,
    liveReload: true
  }
}