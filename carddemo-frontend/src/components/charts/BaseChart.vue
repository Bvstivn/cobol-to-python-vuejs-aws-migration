<template>
  <div class="base-chart">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import {
  Chart,
  type ChartConfiguration,
  type ChartType,
  registerables
} from 'chart.js'

// Registrar todos los componentes de Chart.js
Chart.register(...registerables)

interface Props {
  type: ChartType
  data: ChartConfiguration['data']
  options?: ChartConfiguration['options']
}

const props = withDefaults(defineProps<Props>(), {
  options: () => ({})
})

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

// Opciones por defecto con soporte para tema oscuro
const defaultOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: true,
      position: 'bottom' as const,
      labels: {
        color: 'rgb(156, 163, 175)', // gray-400
        font: {
          family: 'Inter, system-ui, sans-serif',
          size: 12
        },
        padding: 16,
        usePointStyle: true
      }
    },
    tooltip: {
      enabled: true,
      backgroundColor: 'rgba(17, 24, 39, 0.95)', // gray-900
      titleColor: 'rgb(243, 244, 246)', // gray-100
      bodyColor: 'rgb(229, 231, 235)', // gray-200
      borderColor: 'rgb(75, 85, 99)', // gray-600
      borderWidth: 1,
      padding: 12,
      cornerRadius: 8,
      titleFont: {
        size: 14,
        weight: 'bold' as const
      },
      bodyFont: {
        size: 13
      }
    }
  }
}))

// Combinar opciones por defecto con las proporcionadas
const mergedOptions = computed(() => {
  return {
    ...defaultOptions.value,
    ...props.options,
    plugins: {
      ...defaultOptions.value.plugins,
      ...(props.options?.plugins || {})
    }
  }
})

function createChart() {
  if (!chartCanvas.value) return

  // Destruir instancia anterior si existe
  if (chartInstance) {
    chartInstance.destroy()
  }

  // Crear nueva instancia
  chartInstance = new Chart(chartCanvas.value, {
    type: props.type,
    data: props.data,
    options: mergedOptions.value
  })
}

function updateChart() {
  if (!chartInstance) return

  // Actualizar datos
  chartInstance.data = props.data
  chartInstance.options = mergedOptions.value
  chartInstance.update()
}

onMounted(() => {
  createChart()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

// Observar cambios en los datos y opciones
watch(() => props.data, () => {
  updateChart()
}, { deep: true })

watch(() => props.options, () => {
  updateChart()
}, { deep: true })

// Exponer método para actualizar manualmente
defineExpose({
  updateChart,
  getChartInstance: () => chartInstance
})
</script>

<style scoped>
.base-chart {
  position: relative;
  width: 100%;
  height: 100%;
}

canvas {
  max-width: 100%;
  height: auto !important;
}
</style>
