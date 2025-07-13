<template>
  <div class="module-container">
    <div class="header">
      <h1 class="title">智能分析建议</h1>
      <RouterLink to="/" class="back-button">返回首页</RouterLink>
    </div>

    <div class="grid-options">
      <RouterLink to="/intelligence/summary" class="card gradient-navy">
        <img src="@/assets/intelligent-summary.png" alt="summary" />
        <div class="label">运营建议</div>
      </RouterLink>

      <RouterLink to="/intelligence/qa" class="card gradient-cyan">
        <img src="@/assets/intelligent-qa.png" alt="qa" />
        <div class="label">智能问答</div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.module-container {
  padding: 40px 60px;
  background: linear-gradient(to bottom, #eef3f9, #dce8f6);
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

.grid-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 40px;
  margin-top: 20px;
}

.card {
  border-radius: 16px;
  padding: 32px 16px;
  text-align: center;
  background-color: white;
  text-decoration: none;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card:hover {
  transform: translateY(-5px);
}

.card img {
  width: 120px;
  height: 120px;
  margin-bottom: 16px;
}

.label {
  font-size: 1.2rem;
  font-weight: bold;
  color: #2c3e50;
}

.gradient-navy {
  background: linear-gradient(135deg, #2980b9 0%, #5d6d7e 100%);
}

.gradient-cyan {
  background: linear-gradient(135deg, #1abc9c 0%, #48c9b0 100%);
}
</style>
