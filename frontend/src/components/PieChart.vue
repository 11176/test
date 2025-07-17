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
    title: {
      text: '城市销售额占比',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const total = props.data.datasets[0].data.reduce((a, b) => a + b, 0)
        const percent = ((params.value / total) * 100).toFixed(1)
        return `
          <div style="font-weight:bold">${params.name}</div>
          <div>销售额: ¥${params.value.toLocaleString()}</div>
          <div>占比: ${percent}%</div>
        `
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'middle',
      data: props.data.labels
    },
    series: [
      {
        name: '城市销售',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b|{b}}\n{c|¥{c}}',
          rich: {
            b: {
              fontSize: 12,
              fontWeight: 'bold',
              padding: [0, 0, 5, 0]
            },
            c: {
              color: '#409eff',
              fontSize: 11
            }
          }
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: props.data.labels.map((label, index) => ({
          value: props.data.datasets[0].data[index],
          name: label,
          itemStyle: {
            color: props.data.datasets[0].backgroundColor[index]
          }
        }))
      }
    ]
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