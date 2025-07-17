<template>
  <div class="api-test">
    <h2>后端API测试</h2>
    
    <div class="controls">
      <button @click="testConnection" class="btn">测试连接</button>
      <button @click="fetchData" class="btn">获取真实数据</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- 测试接口结果 -->
    <div v-if="testResult" class="result">
      <h3>测试结果：</h3>
      <pre>{{ testResult }}</pre>
    </div>

    <!-- 真实数据展示 -->
    <div v-if="cityData" class="data-display">
      <h3>城市数据 (共 {{ cityData.length }} 条)</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in cityData" :key="index">
            <td v-for="col in columns" :key="col">
              <template v-if="Array.isArray(item[col])">
                {{ item[col].join(', ') }}
              </template>
              <template v-else>
                {{ item[col] || 'null' }}
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      loading: false,
      error: null,
      testResult: null,
      cityData: null,
      columns: []
    }
  },
  methods: {
    async testConnection() {
      try {
        this.loading = true
        //const response = await axios.get('http://localhost:5000/api/trade/test')
        const response = await axios.get('/api/trade/test')
        this.testResult = response.data
        this.error = null
      } catch (err) {
        this.error = `连接失败: ${err.message}`
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async fetchData() {
      try {
        this.loading = true
        //const response = await axios.get('http://localhost:5000/api/trade/analyze-location')
        const response = await axios.get('/api/trade/analyze-location')
        if (response.data?.data?.city_summary) {
          this.columns = response.data.data.city_summary.columns
          this.cityData = response.data.data.city_summary.data
        }
        this.error = null
      } catch (err) {
        this.error = `获取数据失败: ${err.message}`
        console.error(err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.api-test {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.controls {
  margin: 20px 0;
}

.btn {
  padding: 8px 16px;
  margin-right: 10px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.loading, .error {
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
}

.loading {
  background: #f8f8f8;
  color: #666;
}

.error {
  background: #ffebee;
  color: #f44336;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.data-table th, .data-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.data-table th {
  background-color: #f2f2f2;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
