<template>
  <div class="portrait-container">
    <header class="header-bar">
      <h1 class="logo">网店运营数据智能分析系统</h1>
      <button class="back-button" @click="$router.back()">返回</button>
    </header>

    <div class="content-box">
      <div class="tab-buttons">
        <button @click="activeTab = 'province'" :class="{ active: activeTab === 'province' }">省份地域分析</button>
        <button @click="activeTab = 'city'" :class="{ active: activeTab === 'city' }">城市地域分析</button>
        <button @click="activeTab = 'district'" :class="{ active: activeTab === 'district' }">县区地域分析</button>
      </div>

      <!-- ✅ 省份地域分析 -->
      <div v-if="activeTab === 'province'" class="data-card">
        <h2>省份销售额占比</h2>
        <BaseChart :data="provinceData" title="省份销售额占比" />

        <div class="filter-bar">
          <label>选择省份：</label>
          <select v-model="selectedProvince">
            <option v-for="item in provinceData" :key="item.name" :value="item.name">{{ item.name }}</option>
          </select>

          <input type="text" v-model="searchKeyword" placeholder="搜索商品名称" />
        </div>

        <table class="product-table" v-if="paginatedProducts.length">
          <thead>
            <tr>
              <th @click="sortBy('name')">商品名称</th>
              <th @click="sortBy('sales')">销量</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedProducts" :key="item.name">
              <td>{{ item.name }}</td>
              <td>{{ item.sales }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="totalPages > 1" class="pagination">
          <button :disabled="currentPage === 1" @click="currentPage--">上一页</button>
          <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
          <button :disabled="currentPage === totalPages" @click="currentPage++">下一页</button>
        </div>
      </div>

<!-- ✅ 城市地域分析 -->
<div v-if="activeTab === 'city'" class="data-card">
  <h2>城市销售额占比</h2>

  <!-- 筛选省份 / Top10 -->
  <div class="filter-bar">
    <label>选择省份：</label>
    <select v-model="selectedCityProvince">
      <option value="">全部省份</option>
      <option v-for="prov in provinceList" :key="prov" :value="prov">{{ prov }}</option>
    </select>

    <button @click="showTop10Only = !showTop10Only">
      {{ showTop10Only ? '显示全部城市' : '只显示Top10城市' }}
    </button>
  </div>

  <BaseChart :data="filteredCityData" title="城市销售额占比" />

  <!-- 城市畅销商品筛选 -->
  <div class="filter-bar" style="margin-top: 40px;">
    <label>选择省份：</label>
    <select v-model="cityProductProvince">
      <option disabled value="">请选择省份</option>
      <option v-for="prov in provinceList" :key="prov" :value="prov">{{ prov }}</option>
    </select>

    <label>选择城市：</label>
    <select v-model="selectedCity">
      <option v-for="city in cityListByProvince" :key="city" :value="city">{{ city }}</option>
    </select>
  </div>

  <table class="product-table" v-if="cityHotProducts[selectedCity]">
    <thead>
      <tr>
        <th>商品名称</th>
        <th>销量</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in cityHotProducts[selectedCity]" :key="index">
        <td>{{ item.name }}</td>
        <td>{{ item.sales }}</td>
      </tr>
    </tbody>
  </table>
</div>

     <!-- ✅ 县区地域分析 -->
<div v-if="activeTab === 'district'" class="data-card">
  <h2>县区销售额占比</h2>

  <!-- 筛选栏 -->
  <div class="select-box">
    <label>显示模式：</label>
    <select v-model="districtMode">
      <option value="top3">Top3</option>
      <option value="all">全部</option>
    </select>

    <label>选择省份：</label>
    <select v-model="selectedDistrictProvince">
      <option value="">全部省份</option>
      <option v-for="p in districtProvinceList" :key="p">{{ p }}</option>
    </select>

    <label>选择城市：</label>
    <select v-model="selectedDistrictCity">
      <option value="">全部城市</option>
      <option v-for="c in districtCityListByProvince" :key="c">{{ c }}</option>
    </select>
  </div>

  <!-- 图表展示 -->
  <BaseChart :data="filteredDistrictData" title="县区销售额占比" />
</div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import BaseChart from '@/components/BaseChart.vue'

const activeTab = ref('province')
const provinceData = ref([])
const cityData = ref([])
const districtData = ref([])

// 省份畅销商品相关
const selectedProvince = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = 5
const sortKey = ref('sales')
const sortAsc = ref(false)
const hotProducts = ref({})

// 城市筛选/Top10
const selectedCityProvince = ref('')
const showTop10Only = ref(false)
const provinceList = ref([])
const cityHotProducts = ref({})
const cityProductProvince = ref('')
const selectedCity = ref('')
const cityProvinceMap = ref({})

const districtMode = ref('top3') // 默认显示Top3
const selectedDistrictProvince = ref('') // 默认显示全部省份
const selectedDistrictCity = ref('') // 默认显示全部城市

const districtRawData = ref([])

const districtProvinceList = computed(() => {
  return [...new Set(districtRawData.value.map(i => i['收货人省份']))]
})

// 加载数据
onMounted(async () => {
  const res = await axios.get('http://localhost:5000/api/trade/analyze-location')
  const data = res.data.data

  // 省份销售额
  provinceData.value = data.province_summary.data.map(item => ({
    name: item['收货人省份'],
    value: item['省份总金额']
  }))
  selectedProvince.value = provinceData.value[0]?.name || ''

  // 省份畅销商品解析
  data.province_summary.data.forEach(item => {
    const province = item['收货人省份']
    const products = item['畅销商品'] || []
    hotProducts.value[province] = products.map(str => {
      const match = str.match(/^(.*)\((\d+)\)$/)
      return match ? { name: match[1], sales: +match[2] } : { name: str, sales: 0 }
    })
  })

  // 城市销售额
  cityData.value = data.city_summary.data.map(item => ({
    name: item['收货人城市'],
    value: item['城市总金额'],
    province: item['收货人省份']
  }))
  provinceList.value = [...new Set(cityData.value.map(item => item.province))]

  // 区县销售额
  districtData.value = data.district_summary.data.map(item => ({
    name: item['收货人地区'],
    value: item['地区总金额']
  }))
})

// 省份商品过滤 + 排序
const filteredProducts = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  let list = hotProducts.value[selectedProvince.value] || []

  if (keyword) {
    list = list.filter(p => p.name.toLowerCase().includes(keyword))
  }

  return [...list].sort((a, b) =>
    sortAsc.value
      ? a[sortKey.value] - b[sortKey.value]
      : b[sortKey.value] - a[sortKey.value]
  )
})
const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredProducts.value.slice(start, start + pageSize)
})
const totalPages = computed(() => Math.ceil(filteredProducts.value.length / pageSize))

function sortBy(key) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = false
  }
  currentPage.value = 1
}

// 城市 Top10 / 筛选省份
const filteredCityData = computed(() => {
  let data = [...cityData.value]
  if (selectedCityProvince.value) {
    data = data.filter(item => item.province === selectedCityProvince.value)
  }
  if (showTop10Only.value) {
    data = [...data].sort((a, b) => b.value - a.value).slice(0, 10)
  }
  return data
})
// 城市列表（当前省下的城市）
const cityListByProvince = computed(() => {
  return Object.keys(cityHotProducts.value).filter(
    (city) => cityProvinceMap.value[city] === cityProductProvince.value
  )
})

const districtCityListByProvince = computed(() => {
  return districtRawData.value
    .filter(item => !selectedDistrictProvince.value || item['收货人省份'] === selectedDistrictProvince.value)
    .map(item => item['收货人城市'])
    .filter((v, i, arr) => arr.indexOf(v) === i)
})

const filteredDistrictData = computed(() => {
  let filtered = [...districtRawData.value];

  // 省份筛选
  if (selectedDistrictProvince.value) {
    filtered = filtered.filter(i => i['收货人省份'] === selectedDistrictProvince.value);
  }

  // 城市筛选
  if (selectedDistrictCity.value) {
    filtered = filtered.filter(i => i['收货人城市'] === selectedDistrictCity.value);
  }

  // 映射成图表格式
  const mapped = filtered.map(i => ({
    name: i['收货人地区'],
    value: i['地区总金额']
  }));

  // 模式切换：Top3 或 全部
  if (districtMode.value === 'top3') {
    return mapped.sort((a, b) => b.value - a.value).slice(0, 3);
  }

  return mapped;
});

onMounted(async () => {
  const res = await axios.get('http://localhost:5000/api/trade/analyze-location')
  const data = res.data.data

  // ✅ 城市畅销商品解析
  cityHotProducts.value = {}
  cityProvinceMap.value = {}

  data.city_summary.data.forEach((item) => {
    const city = item['收货人城市']
    const province = item['收货人省份']
    cityProvinceMap.value[city] = province

    const raw = item['畅销商品'] || []
    cityHotProducts.value[city] = raw.map((str) => {
      const match = str.match(/^(.*)\((\d+)\)$/)
      return match ? { name: match[1], sales: +match[2] } : { name: str, sales: 0 }
    })
  })

  districtRawData.value = data.district_summary.data
  
  // 默认联动初始化
  if (!cityProductProvince.value) cityProductProvince.value = provinceList.value[0] || ''
  if (!selectedCity.value) selectedCity.value = cityListByProvince.value[0] || ''
})
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  font-size: 1rem;
  color: #444;
  line-height: 1.8;
  text-align: center;
}
.data-card h2 {
  font-size: 1.4rem;
  margin-bottom: 16px;
  color: #34495e;
}
.filter-bar {
  margin-top: 30px;
  margin-bottom: 10px;
  display: flex;
  gap: 16px;
  justify-content: flex-start;
  align-items: center;
  flex-wrap: wrap;
}
.filter-bar input,
.filter-bar select,
.filter-bar button {
  padding: 6px 12px;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
}
.filter-bar button {
  background-color: #409eff;
  color: #fff;
  border: none;
}
.filter-bar button:hover {
  background-color: #66b1ff;
}
.product-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
.product-table th,
.product-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: center;
}
.product-table th {
  background-color: #f4f8fb;
  color: #34495e;
  font-weight: bold;
  cursor: pointer;
}
.pagination {
  margin-top: 12px;
  text-align: right;
}
.pagination button {
  padding: 6px 12px;
  margin: 0 4px;
  border: none;
  border-radius: 6px;
  background: #409eff;
  color: #fff;
  cursor: pointer;
}
.pagination button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
