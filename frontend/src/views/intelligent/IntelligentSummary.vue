<template>
  <div class="page-container">
    <div class="header">
      <RouterLink to="/intelligence" class="back-button">返回</RouterLink>
      <h1 class="page-title">智能分析</h1>
    </div>

    <div class="content-area">
      <div class="card">
        <h2 class="card-title">一键生成运营建议</h2>
        <button class="generate-btn" @click="generateSummary">生成建议</button>
        <div v-if="summaryText" class="summary-result">
          {{ summaryText }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const summaryText = ref('')

function generateSummary() {
  summaryText.value = '根据当前的销售趋势与用户画像分析，建议优化库存管理并加强高潜力用户营销。';
}
</script>

<style scoped>
.page-container {
  padding: 40px 20px;
  background: linear-gradient(120deg, #f0f4f8 0%, #dfe9f3 100%);
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.back-button {
  font-size: 1rem;
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border-radius: 8px;
  text-decoration: none;
}

.content-area {
  max-width: 800px;
  margin: 0 auto;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.card-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 20px;
}

.generate-btn {
  padding: 10px 20px;
  font-size: 1rem;
  background-color: #67c1ff;
  border: none;
  color: white;
  border-radius: 8px;
  cursor: pointer;
}

.summary-result {
  margin-top: 20px;
  font-size: 1.1rem;
  color: #333;
  background: #f8f8f8;
  padding: 20px;
  border-radius: 12px;
  text-align: left;
}
</style>
