<template>
  <div class="module-container">
    <div class="header">
      <h1 class="title">商品风险分析</h1>
      <RouterLink to="/product" class="back-button">返回</RouterLink>
    </div>

    <div class="content">
      <div class="chart-placeholder">
        <p>【图表1 占位】用于展示商品异常波动情况</p>
      </div>
      <div class="chart-placeholder">
        <p>【图表2 占位】用于展示风险商品详情</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
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
</style>
