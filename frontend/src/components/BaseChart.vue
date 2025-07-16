<template>
  <div class="chart-container">
    <div v-if="loading" class="loading">图表加载中...</div>
    <div v-else-if="!chartData || chartData.length === 0" class="no-data">⚠️ 无图表数据</div>
    <div v-else ref="chartRef" class="chart"></div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: '图表'
  },
  type: {
    type: String,
    default: 'pie' // 目前只处理饼图
  }
})

const chartRef = ref(null)
let chartInstance = null
const loading = ref(true)
const chartData = ref([])

watch(
  () => props.data,
  (newVal) => {
    chartData.value = Array.isArray(newVal) ? newVal : []
    loading.value = false
    if (chartData.value.length) {
      nextTick(initChart)
    }
  },
  { immediate: true }
)

function initChart() {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
    window.addEventListener('resize', () => chartInstance?.resize())
  }
  chartInstance.setOption(generateOption(chartData.value, props.title, props.type))
}

function generateOption(data, title, type) {
  if (type === 'pie') {
    return {
      title: {
        text: title,
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: '5%',
        top: 'middle',
        itemWidth: 12,
        itemHeight: 12,
        textStyle: {
          fontSize: 12
        }
      },
      series: [
        {
          name: title,
          type: 'pie',
          radius: ['40%', '65%'],
          center: ['65%', '50%'],
          avoidLabelOverlap: false,
          label: {
            show: true,
            position: 'outside'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            }
          },
          data
        }
      ]
    }
  }

  if (type === 'bar') {
    return {
      title: {
        text: title,
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: data.map(d => d.name),
        axisLabel: {
          rotate: 30,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: title,
          type: 'bar',
          data: data.map(d => d.value),
          label: {
            show: true,
            position: 'top'
          },
          barMaxWidth: 40
        }
      ]
    }
  }

  // 可选：未来支持折线图（line）
  if (type === 'line') {
    return {
      title: {
        text: title,
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: data.map(d => d.name)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: title,
          type: 'line',
          data: data.map(d => d.value),
          label: {
            show: true,
            position: 'top'
          },
          smooth: true
        }
      ]
    }
  }

  return {}
}

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 600px; /* 关键：足够高度，避免图例遮挡 */
  position: relative;
}

.chart {
  width: 100%;
  height: 100%;
}

.loading,
.no-data {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #888;
  font-size: 16px;
}
</style>
