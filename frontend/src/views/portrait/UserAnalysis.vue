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
<BaseChart :data="valueBarChart" title="客户等级分布柱状图" type="bar" />

        <label style="margin-bottom: 10px; display: inline-block;">
          客户等级筛选：
          <select v-model="selectedSegment">
            <option value="all">全部</option>
            <option value="high">高价值客户（前20%）</option>
            <option value="potential">潜力客户（中间30%）</option>
            <option value="normal">普通客户（后50%）</option>
          </select>
        </label>

        <table>
          <thead>
            <tr>
              <th>用户ID</th>
              <th>总消费金额</th>
              <th>省份</th>
              <th>城市</th>
              <th>订单总数</th>
              <th>平均订单质量</th>
              <th>等级</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in displayedUsers" :key="`user-${u.买家昵称}`">
              <td>{{ u.买家昵称 }}</td>
              
              <td>{{ u.总消费金额 }}</td>
              <td>{{ u.省份 }}</td>
              <td>{{ u.城市 }}</td>
              <td>{{ u.订单总数 }}</td>
              <td>{{ u.平均订单质量 }}</td>
              <td>{{ u.level }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="tab === 'rfm'">
        <h2>RFM 客户分层</h2>
        <BaseChart :data="rfmChartData" title="RFM 客户分布" type="bar" />
        <label style="margin-top: 20px; display: inline-block;">
  客户类型筛选：
  <select v-model="selectedRfmGroup">
  <option value="all">全部</option>
  <option v-for="g in rfmGroups" :key="g" :value="g">{{ g }}</option>
</select>

</label>

<table v-if="selectedRfmGroup !== 'all'">
  <thead>
    <tr>
      <th>买家昵称</th>
      <th>会员等级</th>
      <th>偏好商品</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="u in filteredRfmUsers" :key="`rfm-${u.买家昵称}-${u.脱敏手机号}`">
      <td>{{ u.买家昵称 }}</td>
      <td>{{ u.最新会员等级 || '未知' }}</td>
      <td>{{ u.偏好商品?.join(', ') || '无' }}</td>
    </tr>
  </tbody>
</table>


      </div>

      <div v-else-if="tab === 'level'">
        <h2>客户等级与消费能力</h2>
        <BaseChart :data="levelChartData" title="会员等级人数分布" type="bar" />
        <BaseChart :data="levelConsumptionChartData" title="不同等级平均消费金额" type="bar" />
        <BaseChart :data="levelOrderAvgChartData" title="不同等级平均订单数" type="bar" />
      </div>

      <div v-else-if="tab === 'preference'">
        <h2>偏好商品类型分析</h2>
         <label style="margin-bottom: 10px; display: inline-block;">
    客户等级筛选：
    <select v-model="selectedLevel">
      <option value="全部">全部</option>
      <option v-for="lv in allLevels" :key="lv" :value="lv">{{ lv }}</option>
    </select>
  </label>

  <!-- 新的柱状图（等级维度的关键词频率） -->
  <BaseChart :data="filteredPreferenceData" title="不同客户等级的偏好商品关键词分布" type="bar" />

  <!-- 用户详情表格 -->
  <table style="margin-top: 30px;">
    <thead>
      <tr>
        <th>买家昵称</th>
        <th>会员等级</th>
        <th>偏好商品</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="u in filteredUsers" :key="`pref-${u.买家昵称}-${u.脱敏手机号}`">
        <td>{{ u.买家昵称 }}</td>
        <td>{{ u.最新会员等级 || '未知' }}</td>
        <td>{{ u.偏好商品?.join(', ') || '无' }}</td>
      </tr>
    </tbody>
  </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import BaseChart from '@/components/BaseChart.vue'

const valueBarChart = ref([])
const tab = ref('value')
const rawData = ref([])
const valueSegments = ref({ high: [], potential: [], normal: [] })
const rfmChartData = ref([])
const preferenceChartData = ref([])
const selectedSegment = ref('all')
const selectedRfmGroup = ref('all')
const rfmGroups = ['重要价值客户', '潜力客户', '流失预警客户', '一般客户']

const filteredRfmUsers = computed(() => {
  if (selectedRfmGroup.value === 'all') return []

  return rawData.value.filter(u => {
    const score = u.RFM_score
    switch (selectedRfmGroup.value) {
      case '重要价值客户':
        return score >= 8
      case '潜力客户':
        return score >= 6 && score < 8
      case '流失预警客户':
        return score <= 3
      case '一般客户':
        return score > 3 && score < 6
      default:
        return false
    }
  })
})
const displayedUsers = computed(() => {
  if (selectedSegment.value === 'all') {
    return [
      ...valueSegments.value.high.map(u => ({ ...u, level: '高价值客户' })),
      ...valueSegments.value.potential.map(u => ({ ...u, level: '潜力客户' })),
      ...valueSegments.value.normal.map(u => ({ ...u, level: '普通客户' }))
    ]
  } else {
    const label =
      selectedSegment.value === 'high'
        ? '高价值客户'
        : selectedSegment.value === 'potential'
        ? '潜力客户'
        : '普通客户'
    return valueSegments.value[selectedSegment.value].map(u => ({ ...u, level: label }))
  }
})

const levelChartData = computed(() => {
  const levels = {}
  rawData.value.forEach(u => {
    const lv = u.最新会员等级 === 'nan' ? '非会员' : u.最新会员等级
    levels[lv] = (levels[lv] || 0) + 1
  })
  return Object.entries(levels).map(([name, value]) => ({ name, value }))
})
const levelConsumptionChartData = computed(() => {
  const map = {}
  rawData.value.forEach(u => {
    const lv = u.最新会员等级 === 'nan' ? '非会员' : u.最新会员等级
    if (!map[lv]) map[lv] = { total: 0, count: 0 }
    map[lv].total += u.总消费金额
    map[lv].count += 1
  })
  return Object.entries(map).map(([name, val]) => ({
    name,
    value: Math.round(val.total / val.count)
  }))
})
const levelOrderAvgChartData = computed(() => {
  const map = {}
  rawData.value.forEach(u => {
    const lv = u.最新会员等级 === 'nan' ? '非会员' : u.最新会员等级
    if (!map[lv]) map[lv] = { total: 0, count: 0 }
    map[lv].total += u.订单总数
    map[lv].count += 1
  })
  return Object.entries(map).map(([name, val]) => ({
    name,
    value: Math.round(val.total / val.count)
  }))
})
const selectedLevel = ref('全部')

const allLevels = computed(() => {
  const levels = new Set(rawData.value.map(u =>
    (u.最新会员等级 && u.最新会员等级 !== 'nan') ? u.最新会员等级 : '非会员'
  ))
  return Array.from(levels)
})


const filteredUsers = computed(() => {
  return rawData.value.filter(u => {
    // 原始字段（字符串）
    const lv = (u.最新会员等级 && u.最新会员等级 !== 'nan') ? u.最新会员等级 : '非会员'
    // 如果“全部”，保留所有；否则判断是否等于所选等级
    return selectedLevel.value === '全部' || lv === selectedLevel.value
  })
})


const filteredPreferenceData = computed(() => {
  const map = {}
  filteredUsers.value.forEach(u => {
    u.偏好商品?.forEach(k => {
      map[k] = (map[k] || 0) + 1
    })
  })
  return Object.entries(map).map(([name, value]) => ({ name, value }))
})
onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:5000/api/trade/analyze-user')
  const users = res.data.data.user_profiles
  // ✅ 修复用户 ID 精度丢失问题
users.forEach(u => {
  u.user_id = u.user_id.toString()
})
  rawData.value = users

  // ✅ 按总消费金额进行排序和百分比分段
  const sortedUsers = [...users].sort((a, b) => b.总消费金额 - a.总消费金额)
  const totalCount = sortedUsers.length
  const highEnd = Math.ceil(totalCount * 0.2)
  const potentialEnd = highEnd + Math.ceil(totalCount * 0.3)

  valueSegments.value.high = sortedUsers.slice(0, highEnd)
  valueSegments.value.potential = sortedUsers.slice(highEnd, potentialEnd)
  valueSegments.value.normal = sortedUsers.slice(potentialEnd)

  // ✅ 为柱状图准备等级人数数据
valueBarChart.value = [
  { name: '高价值客户', value: valueSegments.value.high.length },
  { name: '潜力客户', value: valueSegments.value.potential.length },
  { name: '普通客户', value: valueSegments.value.normal.length }
]



  // RFM 图表数据
  const rfmGroup = {}
  users.forEach(u => {
    let label = '一般客户'
    if (u.RFM_score >= 8) label = '重要价值客户'
    else if (u.RFM_score >= 6) label = '潜力客户'
    else if (u.RFM_score <= 3) label = '流失预警客户'
    rfmGroup[label] = (rfmGroup[label] || 0) + 1
  })
  rfmChartData.value = Object.entries(rfmGroup).map(([name, value]) => ({ name, value }))

  // 等级图表数据
  const levels = {}
  users.forEach(u => {
    const lv = u.最新会员等级 === 'nan' ? '未知' : u.最新会员等级
    levels[lv] = (levels[lv] || 0) + 1
  })
  levelChartData.value = Object.entries(levels).map(([name, value]) => ({ name, value }))

  // 偏好商品关键词数据
  const keywordFreq = {}
  users.forEach(u => {
    u.偏好商品.forEach(k => {
      keywordFreq[k] = (keywordFreq[k] || 0) + 1
    })
  })
  preferenceChartData.value = Object.entries(keywordFreq).map(([name, value]) => ({ name, value }))
})
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.content h2 {
  font-size: 1.4rem;
  color: #34495e;
  margin-bottom: 15px;
}

.content label {
  font-size: 14px;
  color: #555;
}

.content table {
  width: 100%;
  margin-top: 20px;
  border-collapse: collapse;
  font-size: 14px;
}

.content th,
.content td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
select {
  margin-left: 8px;
  padding: 4px 8px;
  font-size: 14px;
}

</style>
