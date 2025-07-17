<template>
  <div class="module-container">
    <div class="header">
      <h1 class="title">
        商品关联分析
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
          <div class="chart-controls">
            <div class="threshold-control">
              <label for="supportThreshold">支持度阈值:</label>
              <input
                  type="range"
                  id="supportThreshold"
                  min="0"
                  max="100"
                  step="1"
                  :value="supportThreshold"
                  @input="updateThreshold"
              >
              <span>{{ supportThreshold }}%</span>
            </div>
            <div class="layout-control">
              <label>布局方式:</label>
              <select v-model="layoutType" @change="updateLayout">
                <option value="force">力导向布局</option>
                <option value="circular">环形布局</option>
              </select>
            </div>
          </div>
          <h2>商品关联网络图</h2>
          <div ref="associationChartRef" class="chart-container"></div>
        </div>

        <div class="chart-card">
          <h2>热销商品常购组合</h2>
          <div class="recommendation-container">
            <div
                v-for="(combination, index) in filteredCombinations"
                :key="index"
                class="recommendation-card"
            >
              <div class="combination-header">
                <h3>{{ combination.商品组合 }}</h3>
                <span class="support-badge">{{ combination.支持度 }}</span>
              </div>
              <div class="combination-info">
                <div class="combination-products">
                  <div
                      v-for="(product, pIndex) in combination.商品组合.split(', ')"
                      :key="pIndex"
                      class="product-item"
                  >
                    <div class="product-icon" :style="{ backgroundColor: getProductColor(product) }">
                      {{ product.substring(0, 1) }}
                    </div>
                    <p>{{ product }}</p>
                  </div>
                </div>
                <div class="combination-actions">
                  <button class="action-button" @click="viewCombinationDetails(combination)">查看详情</button>
                  <button class="action-button" @click="addCombinationToCart(combination)">添加组合</button>
                </div>
              </div>
            </div>
          </div>
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

const associationChartRef = ref(null)
const productData = ref([])
const filteredCombinations = ref([])
const loading = ref(true)
const error = ref(null)
const supportThreshold = ref(10) // 默认支持度阈值
const layoutType = ref('force') // 默认力导向布局

// 获取商品关联数据
const fetchData = async () => {
  loading.value = true
  error.value = null

  try {
    // 使用指定端口获取数据
    const response = await axios.get('/api/product/analyze-association')

    if (!response.data || !response.data.data) {
      throw new Error('数据格式不正确')
    }

    // 处理数据
    productData.value = response.data.data.map(item => ({
      ...item,
      supportValue: parseFloat(item.支持度) // 转为数值便于处理
    }))

    // 初始化过滤后的组合
    updateFilteredCombinations()

  } catch (err) {
    console.error('获取数据失败:', err)
    error.value = err
  } finally {
    loading.value = false
  }
}

// 更新过滤后的商品组合
const updateFilteredCombinations = () => {
  filteredCombinations.value = productData.value.filter(
      combination => combination.supportValue >= supportThreshold.value
  )
}

// 更新支持度阈值
const updateThreshold = (event) => {
  supportThreshold.value = parseInt(event.target.value)
  updateFilteredCombinations()
  initAssociationChart() // 重新渲染图表
}

// 更新布局方式
const updateLayout = () => {
  initAssociationChart() // 重新渲染图表
}

// 初始化关联网络图
const initAssociationChart = () => {
  if (!associationChartRef.value) return  // 只检查DOM是否存在，不检查数据

  const chart = echarts.init(associationChartRef.value)

  // 先检查是否有符合条件的组合（这部分必须在最前面）
  if (filteredCombinations.value.length === 0) {
    // 显示空状态
    chart.setOption({
      title: {
        text: '没有符合条件的商品组合',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 16
        }
      },
      legend: { show: false },  // 隐藏图例
      series: [{
        type: 'graph',
        data: [],
        links: []
      }]
    })
    return
  }

  // 构建节点和边的数据（只有当有数据时才执行）
  const nodes = new Set()
  const links = []

  filteredCombinations.value.forEach(combination => {
    const products = combination.商品组合.split(', ')

    // 添加节点
    products.forEach(product => {
      nodes.add(product)
    })

    // 添加边（商品之间的关联）
    for (let i = 0; i < products.length; i++) {
      for (let j = i + 1; j < products.length; j++) {
        links.push({
          source: products[i],
          target: products[j],
          value: combination.supportValue,
          lineStyle: {
            width: combination.supportValue / 5,
            color: getLinkColor(combination.supportValue)
          }
        })
      }
    }
  })

  // 转换节点集合为数组
  const nodeList = Array.from(nodes).map(name => ({
    name,
    symbolSize: 10 + (getProductSupport(name) * 2),
    itemStyle: {
      color: getProductColor(name)
    }
  }))

  // 配置图表
  const option = {
    tooltip: {
      formatter: function(params) {
        if (params.dataType === 'edge') {
          return `${params.source} <-> ${params.target}<br/>支持度: ${params.value}%`
        }
        return params.name
      }
    },
    legend: {
      data: ['商品关联']
    },
    series: [{
      type: 'graph',
      layout: layoutType.value,
      data: nodeList,
      links: links,
      roam: true,
      label: {
        show: true,
        position: 'right'
      },
      force: {
        repulsion: 1000,
        edgeLength: 100
      },
      circular: {
        rotateLabel: true
      }
    }]
  }

  chart.setOption(option)

  // 响应窗口大小变化
  window.addEventListener('resize', () => chart.resize())
}

// 获取商品的总支持度（用于确定节点大小）
const getProductSupport = (productName) => {
  let totalSupport = 0
  filteredCombinations.value.forEach(combination => {
    if (combination.商品组合.includes(productName)) {
      totalSupport += combination.supportValue
    }
  })
  return totalSupport
}

// 获取边的颜色
const getLinkColor = (supportValue) => {
  if (supportValue > 20) return '#f56c6c' // 高支持度红色
  if (supportValue > 15) return '#e6a23c' // 中等支持度橙色
  return '#67c23a' // 低支持度绿色
}

// 获取商品的颜色（基于商品名称哈希）
const getProductColor = (productName) => {
  const hash = productName.split('').reduce((acc, char) => {
    return char.charCodeAt(0) + ((acc << 5) - acc)
  }, 0)
  const colors = [
    '#409eff', '#67c23a', '#e6a23c', '#f56c6c',
    '#909399', '#907ef2', '#5cdbd3', '#f8cb7f'
  ]
  return colors[Math.abs(hash) % colors.length]
}

// 查看组合详情
const viewCombinationDetails = (combination) => {
  // 这里可以实现查看组合详情的逻辑
  console.log('查看组合详情:', combination)

  // 示例：弹出详情对话框
  alert(`组合详情: ${combination.商品组合}\n支持度: ${combination.支持度}`)

}

// 添加组合到购物车
const addCombinationToCart = (combination) => {
  // 这里可以实现添加组合到购物车的逻辑
  console.log('添加组合到购物车:', combination)
  alert(`已添加组合 "${combination.商品组合}" 到购物车`)
}

// 组件挂载后获取数据并初始化图表
onMounted(() => {
  fetchData().then(() => {
    nextTick(() => {
      initAssociationChart()
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
  height: 400px;
  width: 100%;
}

.chart-controls {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  align-items: center;
}

.threshold-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.threshold-control input {
  width: 200px;
}

.layout-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.layout-control select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
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

.recommendation-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.recommendation-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  transition: transform 0.3s ease;
}

.recommendation-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.combination-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.combination-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.support-badge {
  background-color: #e6a23c;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.combination-products {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.product-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.product-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-weight: bold;
  margin-bottom: 6px;
}

.product-item p {
  margin: 0;
  font-size: 0.9rem;
  text-align: center;
}

.combination-actions {
  display: flex;
  gap: 10px;
}

.action-button {
  flex: 1;
  padding: 8px 12px;
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