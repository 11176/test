<template>
  <div class="module-container">
    <div class="header">
      <h1 class="title">
        商品健康度分析
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
          <h2>商品健康指标雷达图</h2>
          <div ref="healthRadarChartRef" class="chart-container"></div>
        </div>

        <div class="chart-card">
          <h2>商品健康评分趋势</h2>
          <div ref="healthTrendChartRef" class="chart-container"></div>
        </div>

        <div class="product-table-container">
          <h2>商品健康度详情</h2>
          <div class="table-controls">
            <div class="search-input">
              <input
                  type="text"
                  v-model="searchQuery"
                  placeholder="搜索商品..."
                  @input="filterProducts"
              >
              <i class="fa fa-search"></i>
            </div>
            <div class="sort-select">
              <select v-model="sortField" @change="sortProducts">
                <option value="healthScore">健康评分</option>
                <option value="profitRate">利润率</option>
                <option value="salesRate">动销率</option>
                <option value="returnRate">退货率</option>
              </select>
              <select v-model="sortOrder" @change="sortProducts">
                <option value="desc">降序</option>
                <option value="asc">升序</option>
              </select>
            </div>
          </div>
          <table class="product-table">
            <thead>
            <tr>
              <th>商品ID</th>
              <th>商品名称</th>
              <th>健康状态</th>
              <th>健康评分</th>
              <th>利润率</th>
              <th>动销率</th>
              <th>退货率</th>
              <th>操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="product in filteredProducts" :key="product.商品ID"
                :class="{ 'high-risk': product.healthStatus === '高风险' }">
              <td>{{ product.商品ID }}</td>
              <td>{{ product.商品名称 }}</td>
              <td>
                  <span class="status-badge"
                        :style="{ backgroundColor: getStatusColor(product.健康状态) }">
                    {{ product.健康状态 }}
                  </span>
              </td>
              <td>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${product.healthScore}%` }"></div>
                  <span class="score-text">{{ product.healthScore.toFixed(1) }}</span>
                </div>
              </td>
              <td>{{ product.利润率 }}</td>
              <td>{{ product.动销率 }}</td>
              <td>{{ product.退货率 }}</td>
              <td>
                <button class="action-button" @click="viewDetails(product)">详情</button>
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
import { ref, onMounted, nextTick, computed } from 'vue'
import { RouterLink } from 'vue-router'
import * as echarts from 'echarts'
import axios from 'axios'

const healthRadarChartRef = ref(null)
const healthTrendChartRef = ref(null)
const productData = ref([])
const filteredProducts = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const sortField = ref('healthScore')
const sortOrder = ref('desc')

// 获取商品健康度数据
const fetchData = async () => {
  loading.value = true
  error.value = null

  try {
    // 使用指定端口获取数据
    const response = await axios.get('/api/product/analyze-health')

    if (!response.data || !response.data.data) {
      throw new Error('数据格式不正确')
    }

    // 处理数据
    productData.value = response.data.data.map(product => ({
      ...product,
      // 计算健康评分（示例算法，可根据实际需求调整）
      healthScore: calculateHealthScore(product),
      // 解析百分比字符串为数值
      profitRate: parseFloat(product.利润率),
      salesRate: parseFloat(product.动销率),
      returnRate: parseFloat(product.退货率)
    }))

    // 初始化过滤后的产品列表
    filteredProducts.value = [...productData.value]

  } catch (err) {
    console.error('获取数据失败:', err)
    error.value = err
  } finally {
    loading.value = false
  }
}

// 计算商品健康评分
const calculateHealthScore = (product) => {
  // 示例评分算法，可根据实际业务需求调整权重
  const profitRate = parseFloat(product.利润率) || 0
  const salesRate = parseFloat(product.动销率) || 0
  const returnRate = parseFloat(product.退货率) || 0

  // 利润率和动销率越高越好，退货率越低越好
  const score = (
      profitRate * 0.4 +  // 利润率权重40%
      salesRate * 0.4 +  // 动销率权重40%
      (100 - returnRate) * 0.2  // 退货率权重20%
  )

  return Math.min(100, Math.max(0, score))  // 确保分数在0-100之间
}

// 获取健康状态对应的颜色
const getStatusColor = (status) => {
  switch(status) {
    case '高风险': return '#f56c6c'
    case '中等风险': return '#e6a23c'
    case '一般商品': return '#67c23a'
    case '优质商品': return '#409eff'
    default: return '#909399'
  }
}

// 初始化健康指标雷达图
const initHealthRadarChart = () => {
  if (!healthRadarChartRef.value || productData.value.length === 0) return

  const chart = echarts.init(healthRadarChartRef.value)

  // 准备雷达图配置
  const option = {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      // 雷达图的指示器，指定各项指标
      indicator: [
        { name: '利润率', max: 100 },
        { name: '动销率', max: 100 },
        { name: '总销售额', max: Math.max(...productData.value.map(p => p.总销售额)) * 1.2 },
        { name: '总销量', max: Math.max(...productData.value.map(p => p.总销量)) * 1.2 },
        { name: '退货率', max: 30 }  // 退货率通常较低，设置合理上限
      ],
      shape: 'circle'
    },
    series: [{
      name: '商品健康指标',
      type: 'radar',
      data: productData.value.map(product => ({
        value: [
          parseFloat(product.利润率),
          parseFloat(product.动销率),
          product.总销售额,
          product.总销量,
          parseFloat(product.退货率)
        ],
        name: product.商品名称
      }))
    }]
  }

  chart.setOption(option)

  // 响应窗口大小变化
  window.addEventListener('resize', () => chart.resize())
}

// 初始化健康评分趋势图
const initHealthTrendChart = () => {
  if (!healthTrendChartRef.value || productData.value.length === 0) return

  const chart = echarts.init(healthTrendChartRef.value)

  // 生成时间序列（示例数据，实际应从后端获取）
  const dates = generateRecentDates(7)

  // 为每种健康状态创建数据
  const statusData = {
    '高风险': Array(dates.length).fill(0),
    '中等风险': Array(dates.length).fill(0),
    '一般商品': Array(dates.length).fill(0),
    '优质商品': Array(dates.length).fill(0)
  }

  // 示例数据，实际应从后端获取
  dates.forEach((date, index) => {
    // 模拟数据波动
    statusData['高风险'][index] = Math.floor(Math.random() * 5) + 3
    statusData['中等风险'][index] = Math.floor(Math.random() * 8) + 5
    statusData['一般商品'][index] = Math.floor(Math.random() * 12) + 10
    statusData['优质商品'][index] = Math.floor(Math.random() * 10) + 8
  })

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['高风险', '中等风险', '一般商品', '优质商品']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '商品数量'
    },
    series: [
      {
        name: '高风险',
        type: 'line',
        data: statusData['高风险'],
        color: '#f56c6c'
      },
      {
        name: '中等风险',
        type: 'line',
        data: statusData['中等风险'],
        color: '#e6a23c'
      },
      {
        name: '一般商品',
        type: 'line',
        data: statusData['一般商品'],
        color: '#67c23a'
      },
      {
        name: '优质商品',
        type: 'line',
        data: statusData['优质商品'],
        color: '#409eff'
      }
    ]
  }

  chart.setOption(option)

  // 响应窗口大小变化
  window.addEventListener('resize', () => chart.resize())
}

// 生成最近n天的日期数组
const generateRecentDates = (n) => {
  const dates = []
  const today = new Date()

  for (let i = n - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    dates.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }))
  }

  return dates
}

// 筛选商品
const filterProducts = () => {
  if (!searchQuery.value.trim()) {
    filteredProducts.value = [...productData.value]
    return
  }

  const query = searchQuery.value.toLowerCase().trim()
  filteredProducts.value = productData.value.filter(product =>
      product.商品ID.toLowerCase().includes(query) ||
      product.商品名称.toLowerCase().includes(query) ||
      product.健康状态.toLowerCase().includes(query)
  )
}

// 排序商品
const sortProducts = () => {
  filteredProducts.value.sort((a, b) => {
    if (sortField.value === 'healthScore') {
      return sortOrder.value === 'asc'
          ? a.healthScore - b.healthScore
          : b.healthScore - a.healthScore
    } else if (sortField.value === 'profitRate') {
      return sortOrder.value === 'asc'
          ? a.profitRate - b.profitRate
          : b.profitRate - a.profitRate
    } else if (sortField.value === 'salesRate') {
      return sortOrder.value === 'asc'
          ? a.salesRate - b.salesRate
          : b.salesRate - a.salesRate
    } else if (sortField.value === 'returnRate') {
      return sortOrder.value === 'asc'
          ? a.returnRate - b.returnRate
          : b.returnRate - a.returnRate
    }
    return 0
  })
}

// 查看商品详情
const viewDetails = (product) => {
  // 这里可以跳转到商品详情页或显示详情弹窗
  console.log('查看商品详情:', product)
  alert(`查看商品详情: ${product.商品名称}`)
}

// 组件挂载后获取数据并初始化图表
onMounted(() => {
  fetchData().then(() => {
    nextTick(() => {
      initHealthRadarChart()
      initHealthTrendChart()
    })
  })
})
</script>

<style scoped>
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

.product-table-container {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.table-controls {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-input {
  position: relative;
  width: 300px;
}

.search-input input {
  width: 100%;
  padding: 8px 30px 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
}

.search-input i {
  position: absolute;
  right: 10px;
  top: 10px;
  color: #999;
}

.sort-select {
  display: flex;
  gap: 10px;
}

.sort-select select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
  background-color: white;
}

.product-table {
  width: 100%;
  border-collapse: collapse;
}

.product-table th, .product-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.product-table th {
  background-color: #f5f7fa;
  font-weight: 600;
}

.product-table tr.high-risk {
  background-color: #fef0f0;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  font-weight: 500;
}

.score-bar {
  position: relative;
  height: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.score-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  transition: width 0.5s ease;
}

.score-text {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  text-align: center;
  font-size: 12px;
  line-height: 16px;
  color: #333;
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