<template>
  <div class="home-container">
    <div class="title-section">
      <h1 class="main-title">网店运营数据智能分析系统</h1>
      <p class="subtitle">一站式解决方案，助力您的业务决策</p>
    </div>

    <div class="navigation-grid">
      <!-- 画像分析 -->
      <RouterLink to="/portrait" class="nav-card gradient-blue">
        <div class="card-content">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h2 class="card-title">画像分析</h2>
          <p class="card-description">了解客户结构、地域分布，精准划分营销策略。</p>
        </div>
      </RouterLink>

      <!-- 商品运营分析 -->
      <RouterLink to="/product" class="nav-card gradient-red">
        <div class="card-content">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <path d="M16 10a4 4 0 0 1-8 0"/>
            </svg>
          </div>
          <h2 class="card-title">商品运营分析</h2>
          <p class="card-description">洞察商品动销数据，挖掘销售潜力与风险商品。</p>
        </div>
      </RouterLink>

      <!-- 智能分析建议 -->
      <RouterLink to="/intelligence" class="nav-card gradient-gold">
        <div class="card-content">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/>
              <path d="m4.93 4.93 1.41 1.41"/>
              <path d="M17.66 17.66l1.41 1.41"/>
              <path d="M2 12h2"/>
              <path d="M20 12h2"/>
              <path d="m6.34 17.66-1.41 1.41"/>
              <path d="m19.07 4.93-1.41 1.41"/>
              <path d="M12 22a7.5 7.5 0 0 0 5-12.5A4.5 4.5 0 0 0 7 9.5a7.5 7.5 0 0 0 5 12.5Z"/>
            </svg>
          </div>
          <h2 class="card-title">智能分析建议</h2>
          <p class="card-description">基于 AI 的智能运营建议与问答支持，提升决策效率。</p>
        </div>
      </RouterLink>
      <RouterLink to="/test" class="nav-card gradient-blue">
        <div class="card-content">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h2 class="card-title">TEST</h2>
          <p class="card-description">测试</p>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  background: linear-gradient(120deg, #f0f4f8 0%, #dfe9f3 100%);
  min-height: 100vh;
}

.title-section {
  text-align: center;
  margin-bottom: 50px;
}

.main-title {
  font-size: 3rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.2rem;
  color: #66788a;
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

.card-icon svg {
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

/* 背景渐变色 */
.gradient-blue {
  background: linear-gradient(135deg, #409eff 0%, #67c1ff 100%);
}

.gradient-red {
  background: linear-gradient(135deg, #e74c3c 0%, #ff7f50 100%);
}

.gradient-gold {
  background: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%);
}
</style>
