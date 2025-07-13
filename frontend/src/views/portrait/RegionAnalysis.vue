<template>
  <div class="portrait-container">
    <header class="header-bar">
      <h1 class="logo">网店运营数据智能分析系统</h1>
      <button class="back-button" @click="$router.back()">返回</button>
    </header>

    <div class="content-box">
      <div class="tab-buttons">
        <button @click="activeTab = 'Proince'" :class="{ active: activeTab === 'activity' }">
          省份地域分析
        </button>
        <button @click="activeTab = 'City'" :class="{ active: activeTab === 'activity' }">
          城市地域分析
        </button>
        <button @click="activeTab = 'Dict'" :class="{ active: activeTab === 'activity' }">
          县区地域分析
        </button>
      </div>

      <div v-if="activeTab === 'Proince'" class="data-card">
        <p>1</p>
      </div>
      <div v-if="activeTab === 'City'" class="data-card">
        <p>1</p>
      </div>
      <div v-if="activeTab === 'Dict'" class="data-card">
        <p>1</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const activeTab = ref('distribution')
</script>

<style scoped>
.portrait-container {
  background: linear-gradient(120deg, #f8fbff 0%, #eaf4fc 100%);
  min-height: 100vh;
  padding: 30px 20px;
  box-sizing: border-box;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.logo {
  font-size: 1.8rem;
  color: #2c3e50;
  font-weight: bold;
}

.back-button {
  background: #409eff;
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background 0.3s;
}

.back-button:hover {
  background: #66b1ff;
}

.content-box {
  max-width: 960px;
  margin: 0 auto;
}

.tab-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.tab-buttons button {
  background: #f0f0f0;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.tab-buttons .active {
  background: #409eff;
  color: white;
  font-weight: bold;
}

.data-card {
  background: #ffffff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  font-size: 1rem;
  color: #444;
  line-height: 1.8;
}

.data-card h2 {
  font-size: 1.4rem;
  margin-bottom: 16px;
  color: #34495e;
}
</style>
