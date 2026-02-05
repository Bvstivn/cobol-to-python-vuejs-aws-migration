<template>
  <BaseChart
    type="pie"
    :data="chartData"
    :options="chartOptions"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'
import type { ChartData, ChartOptions } from 'chart.js'

interface Props {
  labels: string[]
  data: number[]
  backgroundColor?: string[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  backgroundColor: () => [
    'rgb(59, 130, 246)',   // blue-500
    'rgb(16, 185, 129)',   // green-500
    'rgb(245, 158, 11)',   // amber-500
    'rgb(239, 68, 68)',    // red-500
    'rgb(168, 85, 247)',   // purple-500
    'rgb(236, 72, 153)',   // pink-500
    'rgb(14, 165, 233)',   // sky-500
    'rgb(34, 197, 94)',    // green-400
  ]
})

const chartData = computed<ChartData<'pie'>>(() => ({
  labels: props.labels,
  datasets: [{
    data: props.data,
    backgroundColor: props.backgroundColor,
    borderWidth: 2,
    borderColor: 'rgb(255, 255, 255)',
    hoverOffset: 8
  }]
}))

const chartOptions = computed<ChartOptions<'pie'>>(() => ({
  plugins: {
    title: {
      display: !!props.title,
      text: props.title,
      color: 'rgb(107, 114, 128)', // gray-500
      font: {
        size: 16,
        weight: 'bold'
      },
      padding: {
        top: 10,
        bottom: 20
      }
    },
    legend: {
      position: 'bottom',
      labels: {
        padding: 16,
        usePointStyle: true,
        pointStyle: 'circle'
      }
    }
  }
}))
</script>
