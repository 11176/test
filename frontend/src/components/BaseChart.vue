<template>
  <div ref="chartRef" :style="{ width: '100%', height: '400px' }"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import * as echarts from 'echarts';

// 💡 默认样式配置：自动合并到每一个图表中
const defaultOption = {
  backgroundColor: 'transparent',
  title: {
    left: 'center',
    textStyle: {
      color: '#333',
      fontSize: 20,
      fontWeight: 'bold'
    }
  },
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(50, 50, 50, 0.8)',
    textStyle: {
      color: '#fff',
      fontSize: 14
    }
  },
  legend: {
    bottom: 10,
    textStyle: {
      color: '#555',
      fontSize: 12
    }
  },
  grid: {
    top: 50,
    bottom: 40,
    left: 60,
    right: 40
  },
  color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
};

const props = defineProps({
  option: {
    type: Object,
    default: () => ({})
  }
});

// ⬇️ 引用 DOM 和图表实例
const chartRef = ref(null);
let myChart = null;

// 渲染图表（合并默认样式）
const renderChart = () => {
  if (!chartRef.value) return;

  if (!myChart) {
    myChart = echarts.init(chartRef.value);
  }

  const finalOption = {
    ...defaultOption,
    ...props.option,
    title: { ...defaultOption.title, ...props.option.title },
    tooltip: { ...defaultOption.tooltip, ...props.option.tooltip },
    legend: { ...defaultOption.legend, ...props.option.legend },
    grid: { ...defaultOption.grid, ...props.option.grid },
    color: props.option.color || defaultOption.color
  };

  myChart.setOption(finalOption, true);
};

// 响应 option 变化
watch(() => props.option, (newOption) => {
  if (newOption) nextTick(() => renderChart());
}, { deep: true });

// 初始挂载和销毁
onMounted(() => renderChart());
onBeforeUnmount(() => {
  if (myChart) myChart.dispose();
  myChart = null;
  window.removeEventListener('resize', resizeHandler);
});

// 响应式缩放
const resizeHandler = () => {
  if (myChart) myChart.resize();
};
window.addEventListener('resize', resizeHandler);
</script>
