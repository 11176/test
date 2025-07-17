<template>
  <div ref="chartEl" style="width: 100%; height: 100%;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    validator: (value) => {
      return (
        Array.isArray(value?.labels) &&
        Array.isArray(value?.datasets?.[0]?.data) &&
        value.labels.length === value.datasets[0].data.length
      )
    }
  },
  // 可选：是否显示气泡大小比例尺
  showLegend: {
    type: Boolean,
    default: true
  }
})

const chartEl = ref(null)
let chartInstance = null

const initChart = () => {
  if (!props.data || !chartEl.value) return

  // 计算气泡大小范围（动态适应数据）
  const values = props.data.datasets[0].data.map(item => item.value)
  const minVal = Math.min(...values)
  const maxVal = Math.max(...values)
  const bubbleSizeRange = [10, 50] // 气泡最小和最大直径(px)

  chartInstance = echarts.init(chartEl.value)

  const option = {
    title: {
      text: '县区销售分布分析',
      subtext: '气泡大小代表销售额，位置反映订单量与平均金额',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const data = params.data
        return `
          <div style="font-weight:bold;margin-bottom:5px">${data.name}</div>
          <div>订单量: ${data.orderCount}</div>
          <div>平均金额: ¥${data.avgAmount.toLocaleString()}</div>
          <div>总销售额: ¥${data.value.toLocaleString()}</div>
        `
      }
    },
    legend: props.showLegend ? {
      data: ['销售额区间'],
      right: 10,
      top: 20,
      formatter: (name) => {
        return `${name}: ¥${minVal.toLocaleString()} - ¥${maxVal.toLocaleString()}`
      }
    } : undefined,
    grid: {
      top: props.showLegend ? 80 : 60,
      right: 20,
      bottom: 30,
      left: 40,
      containLabel: true
    },
    xAxis: {
      name: '订单数量',
      nameLocation: 'middle',
      nameGap: 25,
      type: 'value',
      axisLabel: {
        formatter: '{value} 单'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    yAxis: {
      name: '平均订单金额',
      nameLocation: 'middle',
      nameGap: 30,
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    visualMap: {
      show: false,
      dimension: 2, // 映射到value字段
      min: minVal,
      max: maxVal,
      inRange: {
        symbolSize: bubbleSizeRange
      }
    },
    series: [
      {
        name: '县区数据',
        type: 'scatter',
        symbolSize: (data) => {
          // 动态计算气泡大小
          const scale = (data[2] - minVal) / (maxVal - minVal)
          return bubbleSizeRange[0] + scale * (bubbleSizeRange[1] - bubbleSizeRange[0])
        },
        data: props.data.labels.map((label, index) => {
          const item = props.data.datasets[0].data[index]
          return {
            name: label,
            value: [
              item.orderCount,    // x轴：订单量
              item.avgAmount,     // y轴：平均金额
              item.totalAmount    // 决定气泡大小：总销售额
            ],
            orderCount: item.orderCount,
            avgAmount: item.avgAmount,
            itemStyle: {
              color: props.data.datasets[0].backgroundColor?.[index] || '#5470c6'
            }
          }
        }),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
          formatter: ({ name }) => name,
          position: 'top',
          fontSize: 10
        }
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