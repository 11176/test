<template>
  <div class="module-container">
    <div class="module-header">
      <h1 class="module-title">商品概览</h1>
      <RouterLink to="/product" class="back-button">返回</RouterLink>
    </div>

    <div class="module-content">
      <!-- 模拟图表内容 -->
      <div class="chart-card">
        <h2>商品销售趋势</h2>
        <div class="placeholder-chart">[ 图表占位 ]</div>
      </div>
      <div class="chart-card">
        <h2>库存状态概览</h2>
        <div class="placeholder-chart">[ 图表占位 ]</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
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

.placeholder-chart {
  height: 200px;
  background-color: #f0f2f5;
  border: 1px dashed #bbb;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}
</style>
