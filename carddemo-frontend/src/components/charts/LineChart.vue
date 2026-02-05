<template>
  <BaseChart
    type="line"
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
  borderColor?: string
  backgroundColor?: string
  title?: string
  fill?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Datos',
  borderColor: 'rgb(59, 130, 246)', // blue-500
  backgroundColor: 'rgba(59, 130, 246, 0.1)', // blue-500 with opacity
  fill: true
})

const chartData = computed<ChartData<'line'>>(() => ({
  labels: props.labels,
  datasets: [{
    label: props.label,
    data: props.data,
    borderColor: props.borderColor,
    backgroundColor: props.backgroundColor,
    fill: props.fill,
    tension: 0.4,
    borderWidth: 2,
    pointRadius: 4,
    pointHoverRadius: 6,
    pointBackgroundColor: props.borderColor,
    pointBorderColor: '#fff',
    pointBorderWidth: 2
  }]
}))

const chartOptions = computed<ChartOptions<'line'>>(() => ({
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
