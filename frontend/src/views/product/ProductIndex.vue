<template>
  <div class="product-index">
    <div class="top-bar">
      <div class="logo">网店运营数据智能分析系统</div>
      <RouterLink to="/" class="back-button">返回主页</RouterLink>
    </div>

    <div class="title">商品运营分析</div>

    <div class="card-grid">
      <RouterLink to="/product/overview" class="card gradient-blue">
        <img src="@/assets/product-overview.png" alt="overview" />
        <div class="label">销售总览</div>
      </RouterLink>

      <RouterLink to="/product/category-rank" class="card gradient-purple">
        <img src="@/assets/product-category.png" alt="category" />
        <div class="label">品类排行</div>
      </RouterLink>

      <RouterLink to="/product/risk" class="card gradient-red">
        <img src="@/assets/product-risk.png" alt="risk" />
        <div class="label">滞销商品识别</div>
      </RouterLink>

      <RouterLink to="/product/health" class="card gradient-gold">
        <img src="@/assets/product-health.png" alt="health" />
        <div class="label">商品健康度分析</div>
      </RouterLink>

      <RouterLink to="/product/association" class="card gradient-orange">
        <img src="@/assets/product-association.png" alt="association" />
        <div class="label">商品关联分析</div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.product-index {
  background: #f4f7fb;
  min-height: 100vh;
  padding: 40px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px 30px;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.back-button {
  background: #409eff;
  color: white;
  padding: 10px 18px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 30px;
  text-align: center;
  color: #2c3e50;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  text-decoration: none;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.07);
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-6px);
}

.card img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 16px;
}

.label {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

/* 渐变背景风格示例 */
.gradient-blue { background: linear-gradient(135deg, #409eff, #67c1ff); }
.gradient-purple { background: linear-gradient(135deg, #a18cd1, #fbc2eb); }
.gradient-red { background: linear-gradient(135deg, #f85032, #e73827); }
.gradient-green { background: linear-gradient(135deg, #56ab2f, #a8e063); }
.gradient-gold { background: linear-gradient(135deg, #f39c12, #f1c40f); }
.gradient-orange { background: linear-gradient(135deg, #f12711, #f5af19); }
</style>
