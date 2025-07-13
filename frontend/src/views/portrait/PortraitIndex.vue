// ✅ 画像分析导航页面（PortraitIndex.vue）
<template>
  <div class="portrait-container">
    <div class="top-bar">
      <h1 class="system-title">网店运营数据智能分析系统</h1>
      <button class="back-button" @click="$router.push('/')">返回主页</button>
    </div>

    <div class="navigation-grid">
      <!-- 用户画像分析 -->
      <RouterLink to="/portrait/user" class="nav-card gradient-blue">
        <div class="card-content">
          <img src="@/assets/user-icon.png" alt="用户画像" class="card-image" />
          <h2 class="card-title">用户画像分析</h2>
          <p class="card-description">订单价值、客户分层、偏好分析等全方位洞察。</p>
        </div>
      </RouterLink>

      <!-- 地区画像分析 -->
      <RouterLink to="/portrait/region" class="nav-card gradient-green">
        <div class="card-content">
          <img src="@/assets/region-icon.png" alt="地区画像" class="card-image" />
          <h2 class="card-title">地区画像分析</h2>
          <p class="card-description">地区分布、活跃度、消费偏好，辅助区域化营销策略。</p>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.portrait-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  background: linear-gradient(120deg, #f0f4f8 0%, #dfe9f3 100%);
  min-height: 100vh;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1200px;
  margin-bottom: 50px;
}

.system-title {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.back-button {
  background: #409eff;
  color: #fff;
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.back-button:hover {
  background: #2b88d9;
}

.navigation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 40px;
  width: 100%;
  max-width: 1200px;
}

.nav-card {
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  text-decoration: none;
  color: #fff;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-image {
  width: 64px;
  height: 64px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.card-description {
  font-size: 1rem;
  color: #f5f5f5;
  line-height: 1.5;
  font-weight: 300;
}

.gradient-blue {
  background: linear-gradient(135deg, #409eff 0%, #67c1ff 100%);
}

.gradient-green {
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
}
</style>
