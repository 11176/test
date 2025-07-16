<template>
  <div class="page-container">
    <div class="header">
      <RouterLink to="/intelligence" class="back-button">返回</RouterLink>
      <h1 class="page-title">智能分析</h1>
    </div>

    <div class="content-area">
      <div class="card">
        <h2 class="card-title">智能生成运营建议</h2>
        <div class="button-group">
          <button class="generate-btn" @click="generateSummary('location')">生成地区分析建议</button>
          <button class="generate-btn" @click="generateSummary('user')">生成用户分析建议</button>
          <button class="generate-btn" @click="generateSummary('product')">生成商品分析建议</button>
        </div>

        <div v-if="loading" class="summary-result">
          正在生成中……
        </div>

        <div v-else-if="summaryText" class="summary-result" v-html="summaryText"></div>

        <div v-else-if="errorMsg" class="summary-result">
          <span style="color: red">{{ errorMsg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'

const summaryText = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function generateSummary(type) {
  loading.value = true
  errorMsg.value = ''
  summaryText.value = ''

  try {
    const resp = await axios.post('/api/deepseek/suggest', {
      question: '请根据当前分析数据，给出运营优化建议，要求以markdown格式返回，内容要具体、可操作。',
      type: type
    })

    if (resp.data.status === 'success') {
      summaryText.value = marked(resp.data.advice)
    } else {
      errorMsg.value = resp.data.message || '接口返回错误'
    }
  } catch (err) {
    console.error(err)
    errorMsg.value = err.response?.data?.message || err.message
  } finally {
    loading.value = false
  }
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
.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
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
.generate-btn:hover {
  background-color: #409eff;
}
.summary-result {
  margin-top: 20px;
  font-size: 1.05rem;
  color: #333;
  background: #f8f8f8;
  padding: 20px;
  border-radius: 12px;
  text-align: left;
}
</style>
