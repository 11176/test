<template>
  <div class="module-container">
    <div class="module-header">
      <h1 class="module-title">
        品类排行
      </h1>
      <RouterLink
        to="/product"
        class="back-button"
      >
        返回
      </RouterLink>
    </div>

    <div class="module-content">
      <div
        v-if="loading"
        class="loading-mask"
      >
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      <div
        v-else-if="error"
        class="error-message"
      >
        <p>数据加载失败: {{ error.message }}</p>
        <button @click="fetchCategoryData">
          重试
        </button>
      </div>
      <div v-else>
        <div class="chart-card">
          <h2>品类销售排行</h2>
          <div class="chart-controls">
            <label>显示维度: </label>
            <select
              v-model="displayDimension"
              @change="updateChart"
            >
              <option value="sales">
                销售额
              </option>
              <option value="quantity">
                销售量
              </option>
            </select>
          </div>
          <div
            ref="categoryChartRef"
            class="chart-container"
            style="height: 400px;"
          ></div>
          <div
            v-if="!hasData"
            class="no-data-message"
          >
            <p>暂无品类数据</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import * as echarts from 'echarts'
import axios from 'axios'

const categoryChartRef = ref(null)
let categoryChart = null
const categoryData = ref(null)
const loading = ref(true)
const error = ref(null)
const displayDimension = ref('sales')
const hasData = ref(false)

// 获取品类分析数据
const fetchCategoryData = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await axios.get('/api/product/analyze-category')
    console.log('API 返回数据:', response.data)

    if (!response.data || !response.data.category2 || response.data.category2.length === 0) {
      throw new Error('数据格式不正确或无品类数据')
    }

    categoryData.value = response.data
    hasData.value = true
  } catch (err) {
    console.error('获取品类数据失败:', err)
    error.value = err
    hasData.value = false
  } finally {
    loading.value = false
    // 确保DOM更新后再初始化图表
    nextTick(() => {
      initCategoryChart()
    })
  }
}

// 初始化品类排行图表
const initCategoryChart = () => {
  try {
    if (!categoryChartRef.value) {
      console.error('图表容器不存在')
      return
    }

    console.log('初始化图表...')

    // 销毁可能存在的旧图表实例
    if (categoryChart) {
      categoryChart.dispose()
      categoryChart = null
    }

    // 创建新的图表实例
    categoryChart = echarts.init(categoryChartRef.value)

    if (!categoryChart) {
      console.error('无法创建ECharts实例')
      return
    }

    console.log('图表实例创建成功')

    // 使用测试数据（仅用于调试）
    // uncomment以下行来使用测试数据
    /*
    const testData = {
      category2: [
        { Category2: '特色拌菜', total_sales: 15368, total_quantity: 562 },
        { Category2: '韩式泡菜', total_sales: 5077, total_quantity: 243 },
        { Category2: '主食', total_sales: 4585, total_quantity: 442 },
        { Category2: '酱类', total_sales: 922, total_quantity: 44 },
        { Category2: '饮品', total_sales: 448, total_quantity: 56 }
      ]
    }
    categoryData.value = testData
    hasData.value = true
    */

    // 检查数据是否存在
    if (!categoryData.value || !categoryData.value.category2 || categoryData.value.category2.length === 0) {
      console.log('无品类数据，显示空状态')
      hasData.value = false
      return
    }

    hasData.value = true
    updateChart()

    // 监听窗口大小变化，调整图表
    const resizeHandler = () => {
      if (categoryChart) {
        categoryChart.resize()
      }
    }

    window.addEventListener('resize', resizeHandler)

    // 返回清理函数
    return () => {
      window.removeEventListener('resize', resizeHandler)
      if (categoryChart) {
        categoryChart.dispose()
        categoryChart = null
      }
    }
  } catch (err) {
    console.error('初始化图表时出错:', err)
    error.value = new Error('图表初始化失败')
  }
}

// 更新图表数据
const updateChart = () => {
  try {
    if (!categoryChart || !categoryData.value || !hasData.value) return

    // 从二级品类数据中提取名称和对应维度的数据
    const categoryItems = categoryData.value.category2 || []

    // 根据选择的维度确定数据和单位
    const dimensionKey = displayDimension.value === 'sales' ? 'total_sales' : 'total_quantity'
    const dimensionName = displayDimension.value === 'sales' ? '销售额' : '销售量'
    const dimensionUnit = displayDimension.value === 'sales' ? '元' : '件'

    // 排序数据（从高到低）
    const sortedItems = [...categoryItems].sort((a, b) => b[dimensionKey] - a[dimensionKey])

    // 准备图表数据
    const categoryNames = sortedItems.map(item => item.Category2)
    const dimensionValues = sortedItems.map(item => item[dimensionKey])

    // 确保有数据
    if (categoryNames.length === 0 || dimensionValues.length === 0) {
      console.log('无有效数据用于图表')
      return
    }

    // 为不同的品类生成不同的颜色
    const colors = [
      '#36A2EB', '#FF6384', '#4BC0C0', '#FFCD56', '#C9CBFF',
      '#FF9F40', '#FF5252', '#7CFC00', '#FF1493', '#BA55D3',
      '#00BFFF', '#FF69B4', '#32CD32', '#DA70D6', '#40E0D0'
    ]

    const option = {
      color: colors,
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params) => {
          const param = params[0]
          return `${param.name}<br/>${dimensionName}: ${param.value.toLocaleString()}${dimensionUnit}`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: categoryNames,
        axisLabel: {
          rotate: 30,
          interval: 0
        }
      },
      yAxis: {
        type: 'value',
        name: dimensionName,
        axisLabel: {
          formatter: (value) => `${value.toLocaleString()}${dimensionUnit}`
        }
      },
      series: [
        {
          name: dimensionName,
          type: 'bar',
          data: dimensionValues,
          itemStyle: {
            borderRadius: [4, 4, 0, 0]
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }

    console.log('设置图表选项:', option)
    categoryChart.setOption(option)
    console.log('图表渲染完成')
  } catch (err) {
    console.error('更新图表时出错:', err)
    error.value = new Error('图表更新失败')
  }
}

// 组件挂载后获取数据并初始化图表
onMounted(() => {
  console.log('组件已挂载，开始获取数据...')
  fetchCategoryData()

  // 组件卸载时清理资源
  onBeforeUnmount(() => {
    console.log('组件即将卸载，清理图表资源...')
    if (categoryChart) {
      categoryChart.dispose()
      categoryChart = null
    }
  })
})
</script>

<style scoped>
/* 保持原有样式不变 */
.module-container {
  padding: 40px;
  background: linear-gradient(120deg, #f9fafe 0%, #eef3f8 100%);
  min-height: 100vh;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.module-title {
  font-size: 2rem;
  color: #34495e;
  font-weight: bold;
}

.back-button {
  background: #409eff;
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.3s;
}

.back-button:hover {
  background: #66b1ff;
}

.module-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 30px;
  position: relative;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.chart-card h2 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 16px;
  text-align: left;
}

.chart-container {
  width: 100%;
  height: 400px; /* 增加高度确保图表有足够空间 */
  border: 1px solid #eee; /* 添加边框以便于调试 */
}

.chart-controls {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  justify-content: flex-end;
}

.chart-controls label {
  margin-right: 8px;
  color: #606266;
}

.chart-controls select {
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  color: #303133;
}

.loading-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
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
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  padding: 20px;
  text-align: center;
}

.error-message button {
  margin-top: 16px;
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.error-message button:hover {
  background-color: #66b1ff;
}

.no-data-message {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>