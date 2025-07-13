<template>
  <div ref="chartEl" style="width: 100%; height: 100%;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const chartEl = ref(null)
let chartInstance = null

const initChart = () => {
  if (!props.data || !chartEl.value) return
  
  chartInstance = echarts.init(chartEl.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const data = params[0]
        return `
          <strong>${data.name}</strong><br/>
          销售额: ¥${data.value.toLocaleString()}<br/>
          占比: ${((data.value / props.data.datasets[0].data.reduce((a, b) => a + b, 0)) * 100).toFixed(1)}%
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.data.labels,
      axisLabel: {
        rotate: 30,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '销售额',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [{
      name: '省份销售额',
      type: 'bar',
      barWidth: '60%',
      data: props.data.labels.map((label, index) => ({
        value: props.data.datasets[0].data[index],
        name: label,
        itemStyle: {
          color: props.data.datasets[0].backgroundColor[index]
        }
      })),
      label: {
        show: true,
        position: 'top',
        formatter: '¥{c}'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  chartInstance.setOption(option)
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chartInstance?.resize())
})

watch(() => props.data, initChart, { deep: true })

defineExpose({
  resize: () => chartInstance?.resize()
})
</script>