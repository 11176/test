<template>
  <div class="submodule-container">
    <div class="header">
      <h1 class="logo">网店运营数据智能分析系统</h1>
      <button class="back-button" @click="$router.back()">返回</button>
    </div>

    <div class="tabs">
      <button :class="{ active: tab === 'value' }" @click="tab = 'value'">订单价值与客户潜力</button>
      <button :class="{ active: tab === 'rfm' }" @click="tab = 'rfm'">RFM 客户分层</button>
      <button :class="{ active: tab === 'level' }" @click="tab = 'level'">客户等级与消费能力</button>
      <button :class="{ active: tab === 'preference' }" @click="tab = 'preference'">偏好商品类型分析</button>
    </div>

    <div class="content">
      <div v-if="tab === 'value'">
        <h2>订单价值与客户潜力</h2>
        <ul>
          <li>高价值客户（订单金额 ≥ 5000 元）：56 人</li>
          <li>潜力客户（订单金额 2000~5000 元）：132 人</li>
          <li>普通客户（订单金额 ＜ 2000 元）：304 人</li>
        </ul>
      </div>

      <div v-else-if="tab === 'rfm'">
        <h2>RFM 客户分层</h2>
        <ul>
          <li>重要价值客户：36 人</li>
          <li>潜力客户：78 人</li>
          <li>流失预警客户：102 人</li>
          <li>一般客户：276 人</li>
        </ul>
      </div>

      <div v-else-if="tab === 'level'">
        <h2>客户等级与消费能力</h2>
        <ul>
          <li>会员等级：普通 320 人，高级 120 人，VIP 52 人</li>
          <li>订单层级：活跃用户（≥10 单）58 人；中等（5~10 单）142 人；低频（＜5 单）292 人</li>
          <li>平均订单金额：VIP ¥643；普通 ¥321</li>
        </ul>
      </div>

      <div v-else-if="tab === 'preference'">
        <h2>偏好商品类型分析</h2>
        <ul>
          <li>关键词提取：耳机、运动鞋、咖啡机、登山包、键盘、护肤</li>
          <li>高频偏好类型：电子产品、运动户外、个护美妆</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const tab = ref('value')
</script>

<style scoped>
.submodule-container {
  padding: 40px 20px;
  background: linear-gradient(to bottom, #f0f4f8, #ffffff);
  min-height: 100vh;
}

.header {
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
  background-color: #409eff;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #66b1ff;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  background: #e0e6ed;
  color: #333;
  cursor: pointer;
  transition: all 0.3s;
}

.tabs button.active {
  background: #409eff;
  color: white;
  font-weight: bold;
}

.content {
  background: #ffffff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.content h2 {
  font-size: 1.4rem;
  color: #34495e;
  margin-bottom: 15px;
}

.content ul {
  padding-left: 20px;
  line-height: 1.8;
  color: #555;
  font-size: 1rem;
}
</style>
