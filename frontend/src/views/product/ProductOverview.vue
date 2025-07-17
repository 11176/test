<template>
  <div class="module-container">
    <div class="module-header">
      <h1 class="module-title">销售总览</h1>
      <RouterLink to="/product" class="back-button">返回</RouterLink>
    </div>

    <div class="module-content">
      <!-- 图表区域：3列展示 -->
      <div class="chart-grid">
        <!-- 图表1：总销售额 -->
        <div class="chart-card">
          <div class="pagination-controls">
            <button @click="prevPage1" :disabled="page1 === 1">上一页</button>
            <span>第 {{ page1 }} 页 / 共 {{ totalPages1 }} 页</span>
            <button @click="nextPage1" :disabled="page1 === totalPages1">下一页</button>
          </div>
          <BaseChart
            :data="pagedData1.map(item => ({ name: item.ProductName, value: item.total_sales }))"
            title="各商品总销售额"
            type="bar"
          />
        </div>

        <!-- 图表2：平均销售额 -->
        <div class="chart-card">
          <div class="pagination-controls">
            <button @click="prevPage2" :disabled="page2 === 1">上一页</button>
            <span>第 {{ page2 }} 页 / 共 {{ totalPages2 }} 页</span>
            <button @click="nextPage2" :disabled="page2 === totalPages2">下一页</button>
          </div>
          <BaseChart
            :data="pagedData2.map(item => ({ name: item.ProductName, value: item.avg_sales }))"
            title="平均销售额"
            type="bar"
          />
        </div>

        <!-- 图表3：销售高峰时间 -->
        <div class="chart-card">
          <div class="pagination-controls">
            <button @click="prevPage3" :disabled="page3 === 1">上一页</button>
            <span>第 {{ page3 }} 页 / 共 {{ totalPages3 }} 页</span>
            <button @click="nextPage3" :disabled="page3 === totalPages3">下一页</button>
          </div>
          <BaseChart
            :data="pagedData3.map(item => ({ name: item.ProductName, value: item.peak_hour }))"
            title="销售高峰时段"
            type="bar"
          />
        </div>
      </div>

      <!-- 表格区域 -->
      <div class="table-section">
        <h2>商品销售详情</h2>
        <table class="detail-table">
          <thead>
            <tr>
              <th>商品名</th>
              <th>订单数</th>
              <th>平均销售额</th>
              <th>销售总额</th>
              <th>销售总量</th>
              <th>高峰时段</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in salesData" :key="item.ProductID">
              <td>{{ item.ProductName }}</td>
              <td>{{ item.order_count }}</td>
              <td>{{ item.avg_sales.toFixed(2) }}</td>
              <td>{{ item.total_sales }}</td>
              <td>{{ item.total_quantity }}</td>
              <td>{{ item.peak_hour }} 点</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import BaseChart from '@/components/BaseChart.vue'

const salesData = ref([])

onMounted(async () => {
  const res = await axios.get('http://localhost:5000/api/product/analyze-sales')
  salesData.value = res.data.data.sort((a, b) => b.total_sales - a.total_sales)
})

const pageSize = 10
const page1 = ref(1)
const page2 = ref(1)
const page3 = ref(1)

const totalPages1 = computed(() => Math.ceil(salesData.value.length / pageSize))
const totalPages2 = computed(() => Math.ceil(salesData.value.length / pageSize))
const totalPages3 = computed(() => Math.ceil(salesData.value.length / pageSize))

const pagedData1 = computed(() => {
  const start = (page1.value - 1) * pageSize
  return salesData.value.slice(start, start + pageSize)
})
const pagedData2 = computed(() => {
  const start = (page2.value - 1) * pageSize
  return salesData.value.slice(start, start + pageSize)
})
const pagedData3 = computed(() => {
  const start = (page3.value - 1) * pageSize
  return salesData.value.slice(start, start + pageSize)
})

const prevPage1 = () => { if (page1.value > 1) page1.value-- }
const nextPage1 = () => { if (page1.value < totalPages1.value) page1.value++ }
const prevPage2 = () => { if (page2.value > 1) page2.value-- }
const nextPage2 = () => { if (page2.value < totalPages2.value) page2.value++ }
const prevPage3 = () => { if (page3.value > 1) page3.value-- }
const nextPage3 = () => { if (page3.value < totalPages3.value) page3.value++ }
</script>

<style scoped>
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
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 30px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  text-align: center;
}

.chart-card h2 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 16px;
}

.table-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.table-section h2 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 16px;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.detail-table th,
.detail-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

.detail-table th {
  background-color: #f4f6f8;
  font-weight: bold;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 12px;
  gap: 10px;
}

.pagination-controls button {
  background: #409eff;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
}

.pagination-controls button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>