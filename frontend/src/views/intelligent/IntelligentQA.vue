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

      <div class="response-section" v-if="answer">
        <h2>系统回答：</h2>
        <p class="answer-text">{{ answer }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const question = ref('')
const answer = ref('')

function submitQuestion() {
  // 这里暂时是模拟返回结果，未来可接后端 API
  answer.value = '这是一个模拟回答。实际运行时会根据后端模型返回智能回答。'
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
}
</style>
