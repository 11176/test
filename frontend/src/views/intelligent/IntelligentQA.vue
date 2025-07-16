<template>
  <div class="qa-container">
    <div class="header">
      <h1 class="title">智能问答助手</h1>
      <RouterLink to="/intelligence" class="back-button">返回</RouterLink>
    </div>

    <div class="qa-content">
      <div class="input-section">
        <textarea
          v-model="question"
          placeholder="请输入您想了解的运营问题，例如“哪些商品销量下滑？”"
        ></textarea>
        <button class="submit-button" @click="submitQuestion">发送提问</button>
      </div>

      <div class="response-section" v-if="loading">
        <p class="answer-text">正在生成回答，请稍候...</p>
      </div>

      <div class="response-section" v-else-if="answerMarkdown">
        <h2>系统回答：</h2>
        <div class="answer-text" v-html="answerMarkdown"></div>
      </div>

      <div class="response-section" v-else-if="errorMsg">
        <p class="answer-text" style="color:red">{{ errorMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'

const question = ref('')
const answer = ref('')
const errorMsg = ref('')
const loading = ref(false)

const answerMarkdown = computed(() => marked(answer.value || ''))

async function submitQuestion() {
  if (!question.value.trim()) {
    errorMsg.value = '请输入问题内容'
    return
  }

  loading.value = true
  errorMsg.value = ''
  answer.value = ''

  try {
    const resp = await axios.post('/api/deepseek/suggest', {
      question: question.value
    })

    if (resp.data.status === 'success') {
      answer.value = resp.data.advice
    } else {
      errorMsg.value = resp.data.message || '接口返回错误'
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.message || err.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.qa-container {
  padding: 40px 20px;
  background: linear-gradient(to bottom right, #f0f4f8, #dfe9f3);
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.title {
  font-size: 2.2rem;
  font-weight: bold;
  color: #2c3e50;
}

.back-button {
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #2980b9;
}

.qa-content {
  max-width: 800px;
  margin: 0 auto;
  background-color: #fff;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
}

.input-section textarea {
  width: 100%;
  height: 120px;
  padding: 15px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  resize: vertical;
  margin-bottom: 20px;
}

.submit-button {
  padding: 10px 24px;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}

.submit-button:hover {
  background-color: #1e874b;
}

.response-section {
  margin-top: 30px;
}

.answer-text {
  font-size: 1.1rem;
  color: #333;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ddd;
  text-align: left;
  line-height: 1.6;
}
</style>
