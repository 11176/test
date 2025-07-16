import request from './request';

/**
 * @description 这就是 CustomerAnalysis.vue 想要导入的函数
 * 获取图表数据的函数 (目前是模拟)
 * @param {object} params - 请求参数
 */
export function getChartData(params) {
  // 注意：这里返回的是一个 Promise
  // 真实场景下，你会调用 request 发起网络请求
  // return request({
  //   url: '/dashboard/chart', // 后端接口地址
  //   method: 'get',
  //   params
  // });

  // 为了让页面能跑起来，我们暂时先返回一个模拟的 Promise
  // 1秒后返回模拟数据
  console.log("正在调用模拟的 getChartData API，参数：", params);
  return new Promise(resolve => {
    setTimeout(() => {
      const mockData = {
        categories: ['18-24岁', '25-34岁', '35-44岁', '45-54岁', '55+岁'],
        values: [320, 580, 450, 210, 110]
      };
      resolve(mockData);
    }, 1000);
  });
}