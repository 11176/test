<template>
  <div style="padding: 30px">
    <h2>图表测试</h2>
    <BaseChart :chartData="testData" type="pie" title="省份销售额占比" />
  </div>
</template>

<script setup>
import BaseChart from '@/components/BaseChart.vue'

const testData = {
  labels: ['辽宁省', '山东省', '天津市', '北京市', '河北省'],
  values: [6427.56, 3162.7, 2913.3, 2654, 2370.24]
}
</script>
