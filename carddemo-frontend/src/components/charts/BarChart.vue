<template>
  <BaseChart
    type="bar"
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
  label?: string
  backgroundColor?: string
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Datos',
  backgroundColor: 'rgb(59, 130, 246)' // blue-500
})

const chartData = computed<ChartData<'bar'>>(() => ({
  labels: props.labels,
  datasets: [{
    label: props.label,
    data: props.data,
    backgroundColor: props.backgroundColor,
    borderRadius: 6,
    borderSkipped: false
  }]
}))

const chartOptions = computed<ChartOptions<'bar'>>(() => ({
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
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(156, 163, 175, 0.1)', // gray-400 with opacity
        drawBorder: false
      },
      ticks: {
        color: 'rgb(156, 163, 175)', // gray-400
        font: {
          size: 11
        }
      }
    },
    x: {
      grid: {
        display: false,
        drawBorder: false
      },
      ticks: {
        color: 'rgb(156, 163, 175)', // gray-400
        font: {
          size: 11
        }
      }
    }
  }
}))
</script>
