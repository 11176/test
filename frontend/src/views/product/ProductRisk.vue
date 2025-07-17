<template>
  <div class="module-container">
    <div class="header">
      <h1 class="title">
        滞销商品识别
      </h1>
      <RouterLink
          to="/product"
          class="back-button"
      >
        返回
      </RouterLink>
    </div>

    <div class="content">
      <div v-if="loading" class="loading-mask">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else-if="error" class="error-message">
        <p>数据加载失败: {{ error.message }}</p>
        <button @click="fetchData">重试</button>
      </div>
      <div v-else>
        <div class="chart-card">
          <h2>商品异常波动情况</h2>
          <div ref="fluctuationChartRef" class="chart-container"></div>
        </div>
        <!-- 新增风险标准说明卡片 -->
        <div class="risk-criteria-card">
          <h2>风险等级评判标准</h2>
          <div class="criteria-items">
            <div class="criteria-item" :style="{ borderLeftColor: getRiskColor('高') }">
              <div class="criteria-header">
        <span class="risk-badge" :style="{ backgroundColor: getRiskColor('高') }">
          高风险
        </span>
                <span class="criteria-value">取消率 > 30%</span>
              </div>
              <p class="criteria-desc">
                该类商品取消率极高，存在严重质量问题或市场需求不足，需要立即处理
              </p>
            </div>

            <div class="criteria-item" :style="{ borderLeftColor: getRiskColor('中') }">
              <div class="criteria-header">
        <span class="risk-badge" :style="{ backgroundColor: getRiskColor('中') }">
          中风险
        </span>
                <span class="criteria-value">20% ≤ 取消率 ≤ 30%</span>
              </div>
              <p class="criteria-desc">
                该类商品取消率较高，可能存在一定问题，建议进行详细分析和优化
              </p>
            </div>

            <div class="criteria-item" :style="{ borderLeftColor: getRiskColor('低') }">
              <div class="criteria-header">
        <span class="risk-badge" :style="{ backgroundColor: getRiskColor('低') }">
          低风险
        </span>
                <span class="criteria-value">取消率 < 20%</span>
              </div>
              <p class="criteria-desc">
                该类商品取消率正常，质量和市场需求稳定，可维持当前策略
              </p>
            </div>
          </div>
        </div>
        <div class="chart-card">
          <h2>风险商品详情</h2>
          <div ref="riskProductsChartRef" class="chart-container"></div>
        </div>

        <div class="risk-table-container">
          <h2>风险商品列表</h2>
          <table class="risk-table">
            <thead>
            <tr>
              <th>商品ID</th>
              <th>商品名称</th>
              <th>取消率</th>
              <th>风险等级</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="product in highRiskProducts" :key="product.ProductID"
                :class="{ 'high-risk': product.riskLevel === '高' }">
              <td>{{ product.ProductID }}</td>
              <td>{{ product.ProductName }}</td>
              <td>{{ product.取消率 }}</td>
              <td>
                  <span class="risk-badge"
                        :style="{ backgroundColor: getRiskColor(product.riskLevel) }">
                    {{ product.riskLevel }}
                  </span>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import * as echarts from 'echarts'
import axios from 'axios'

const fluctuationChartRef = ref(null)
const riskProductsChartRef = ref(null)
const productData = ref([])
const highRiskProducts = ref([])
const loading = ref(true)
const error = ref(null)

// 获取风险分析数据
const fetchData = async () => {
  loading.value = true
  error.value = null

  try {
    // 使用指定端口获取数据
    const response = await axios.get('/api/product/analyze-cancellation')

    if (!response.data || !response.data.data) {
      throw new Error('数据格式不正确')
    }

    // 处理数据
    productData.value = response.data.data.all_products || []

    // 筛选高风险商品（取消率 > 20%）
    highRiskProducts.value = productData.value
        .filter(product => parseFloat(product.取消率) > 20)
        .map(product => ({
          ...product,
          riskLevel: getRiskLevel(parseFloat(product.取消率))
        }))

  } catch (err) {
    console.error('获取数据失败:', err)
    error.value = err
  } finally {
    loading.value = false
  }
}

// 根据取消率计算风险等级
const getRiskLevel = (cancellationRate) => {
  if (cancellationRate > 30) return '高'
  if (cancellationRate > 20) return '中'
  return '低'
}

// 获取风险等级对应的颜色
const getRiskColor = (riskLevel) => {
  switch(riskLevel) {
    case '高': return '#f56c6c'
    case '中': return '#e6a23c'
    case '低': return '#67c23a'
    default: return '#909399'
  }
}

// 初始化波动图表
// 初始化波动图表（重点修改此函数）
const initFluctuationChart = () => {
  if (!fluctuationChartRef.value || productData.value.length === 0) return

  const chart = echarts.init(fluctuationChartRef.value)

  // 提取数据时过滤掉取消率为0%的商品
  // 重点修改：添加过滤逻辑，只保留取消率 > 0 的商品
  const filteredProducts = productData.value.filter(
      p => parseFloat(p.取消率) > 0
  )

  // 如果过滤后没有数据，显示空状态提示
  if (filteredProducts.length === 0) {
    chart.setOption({
      title: {
        text: '没有非零取消率的商品数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16
        }
      },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value', name: '取消率 (%)' },
      series: [{ type: 'bar', data: [] }]
    })
    return
  }

  // 从过滤后的数据中提取图表所需信息
  const productNames = filteredProducts.map(p => p.ProductName)
  const cancellationRates = filteredProducts.map(p => parseFloat(p.取消率))

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}<br/>取消率: {c}%'
    },
    xAxis: {
      type: 'category',
      data: productNames,
      axisLabel: {
        rotate: 45,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '取消率 (%)',
      min: 0,
      max: 100
    },
    series: [{
      name: '取消率',
      type: 'bar',
      data: cancellationRates,
      itemStyle: {
        color: ({ value }) => {
          if (value > 30) return '#f56c6c'
          if (value > 20) return '#e6a23c'
          return '#67c23a'
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}%'
      }
    }]
  }

  chart.setOption(option)

  // 响应窗口大小变化
  window.addEventListener('resize', () => chart.resize())
}

// 初始化风险商品图表
const initRiskProductsChart = () => {
  if (!riskProductsChartRef.value || highRiskProducts.value.length === 0) return

  const chart = echarts.init(riskProductsChartRef.value)

  // 提取数据
  const highRiskCount = highRiskProducts.value.filter(p => p.riskLevel === '高').length
  const mediumRiskCount = highRiskProducts.value.filter(p => p.riskLevel === '中').length
  const lowRiskCount = productData.value.length - highRiskCount - mediumRiskCount

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      data: ['高风险', '中风险', '低风险']
    },
    series: [{
      name: '风险分布',
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: highRiskCount, name: '高风险', itemStyle: { color: '#f56c6c' } },
        { value: mediumRiskCount, name: '中风险', itemStyle: { color: '#e6a23c' } },
        { value: lowRiskCount, name: '低风险', itemStyle: { color: '#67c23a' } }
      ]
    }]
  }

  chart.setOption(option)

  // 响应窗口大小变化
  window.addEventListener('resize', () => chart.resize())
}

// 组件挂载后获取数据并初始化图表
onMounted(() => {
  fetchData().then(() => {
    nextTick(() => {
      initFluctuationChart()
      initRiskProductsChart()
    })
  })
})
</script>

<style scoped>
/* 新增风险标准卡片样式 */
.risk-criteria-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.criteria-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.criteria-item {
  border-left: 4px solid #999;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 0 8px 8px 0;
  transition: transform 0.3s ease;
}

.criteria-item:hover {
  transform: translateY(-3px);
}

.criteria-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.criteria-value {
  font-weight: 600;
}

.criteria-desc {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.module-container {
  padding: 40px 60px;
  background: linear-gradient(to bottom, #f7f9fc, #e0ecf7);
  min-height: 100vh;
  box-sizing: border-box;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.back-button {
  padding: 8px 16px;
  background-color: #3498db;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.back-button:hover {
  background-color: #2980b9;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.chart-placeholder {
  height: 300px;
  background-color: #ffffff;
  border-radius: 12px;
  border: 2px dashed #ccc;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #999;
  font-size: 1.2rem;
}

.chart-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-5px);
}

.chart-container {
  height: 300px;
  width: 100%;
}

.loading-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.error-message button {
  margin-top: 16px;
  padding: 8px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.risk-table-container {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.risk-table {
  width: 100%;
  border-collapse: collapse;
}

.risk-table th, .risk-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.risk-table th {
  background-color: #f5f7fa;
  font-weight: 600;
}

.risk-table tr.high-risk {
  background-color: #fef0f0;
}

.risk-badge {
  padding: 4px 8px;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  font-weight: 500;
}

.action-button {
  padding: 6px 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.action-button:hover {
  background-color: #2980b9;
}
</style>