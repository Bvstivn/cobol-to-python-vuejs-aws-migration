<template>
  <div class="spending-chart">
    <!-- Header con controles -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Patrones de Gasto
      </h3>
      
      <div v-if="!loading" class="flex items-center gap-2">
        <!-- Selector de período -->
        <select
          v-model="selectedPeriod"
          class="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="week">Semana</option>
          <option value="month">Mes</option>
          <option value="year">Año</option>
        </select>

        <!-- Selector de tipo de gráfico -->
        <div class="flex border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
          <button
            v-for="type in chartTypes"
            :key="type.value"
            @click="selectedChartType = type.value"
            :class="[
              'px-3 py-1.5 text-sm font-medium transition-colors',
              selectedChartType === type.value
                ? 'bg-primary-500 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            ]"
            :title="type.label"
          >
            {{ type.icon }}
          </button>
        </div>
      </div>
    </div>

    <!-- Estado de carga -->
    <div v-if="loading" class="chart-container bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <div class="animate-pulse space-y-4">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
        <div class="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div class="flex justify-center gap-4">
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
        </div>
      </div>
    </div>

    <!-- Estado de error -->
    <div v-else-if="error" class="chart-container bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <div class="flex flex-col items-center justify-center h-64 text-center">
        <svg class="w-16 h-16 text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Error al cargar el gráfico
        </h4>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ error }}
        </p>
        <button
          @click="$emit('retry')"
          class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          Reintentar
        </button>
      </div>
    </div>

    <!-- Estado vacío -->
    <div v-else-if="!data || data.length === 0" class="chart-container bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <div class="flex flex-col items-center justify-center h-64 text-center">
        <svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          No hay datos disponibles
        </h4>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          No se encontraron datos de gastos para el período seleccionado
        </p>
      </div>
    </div>

    <!-- Gráfico -->
    <div v-else class="chart-container bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <component
        :is="currentChartComponent"
        :labels="chartLabels"
        :data="chartData"
        :title="chartTitle"
        v-bind="chartProps"
      />
    </div>

    <!-- Información adicional al hacer hover -->
    <div v-if="hoveredData && !loading && !error" class="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
      <p class="text-sm text-blue-900 dark:text-blue-100">
        <span class="font-semibold">{{ hoveredData.label }}:</span>
        {{ formatCurrency(hoveredData.value) }}
        <span class="text-blue-700 dark:text-blue-300">
          ({{ hoveredData.percentage }}%)
        </span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import BarChart from './BarChart.vue'
import PieChart from './PieChart.vue'
import LineChart from './LineChart.vue'

interface SpendingData {
  category: string
  amount: number
}

interface Props {
  data: SpendingData[]
  period?: 'week' | 'month' | 'year'
  defaultChartType?: 'pie' | 'bar' | 'line'
  loading?: boolean
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  period: 'month',
  defaultChartType: 'pie',
  loading: false,
  error: null
})

const emit = defineEmits<{
  periodChange: [period: 'week' | 'month' | 'year']
  chartTypeChange: [type: 'pie' | 'bar' | 'line']
  dataHover: [data: { label: string; value: number; percentage: number } | null]
  retry: []
}>()

const selectedPeriod = ref(props.period)
const selectedChartType = ref(props.defaultChartType)
const hoveredData = ref<{ label: string; value: number; percentage: number } | null>(null)

const chartTypes = [
  {
    value: 'pie' as const,
    label: 'Gráfico de Pastel',
    icon: '●'
  },
  {
    value: 'bar' as const,
    label: 'Gráfico de Barras',
    icon: '▊'
  },
  {
    value: 'line' as const,
    label: 'Gráfico de Líneas',
    icon: '📈'
  }
]

// Calcular labels y datos del gráfico
const chartLabels = computed(() => props.data.map(item => item.category))
const chartData = computed(() => props.data.map(item => item.amount))

// Calcular total para porcentajes
const totalAmount = computed(() => 
  props.data.reduce((sum, item) => sum + item.amount, 0)
)

// Título del gráfico según el período
const chartTitle = computed(() => {
  const periodLabels = {
    week: 'Esta Semana',
    month: 'Este Mes',
    year: 'Este Año'
  }
  return `Gastos por Categoría - ${periodLabels[selectedPeriod.value]}`
})

// Componente actual según el tipo seleccionado
const currentChartComponent = computed(() => {
  const components = {
    pie: PieChart,
    bar: BarChart,
    line: LineChart
  }
  return components[selectedChartType.value]
})

// Props específicas para cada tipo de gráfico
const chartProps = computed(() => {
  const baseProps = {
    label: 'Gasto'
  }

  if (selectedChartType.value === 'pie') {
    return {
      ...baseProps,
      backgroundColor: [
        'rgb(59, 130, 246)',   // blue-500
        'rgb(16, 185, 129)',   // green-500
        'rgb(245, 158, 11)',   // amber-500
        'rgb(239, 68, 68)',    // red-500
        'rgb(168, 85, 247)',   // purple-500
        'rgb(236, 72, 153)',   // pink-500
        'rgb(14, 165, 233)',   // sky-500
        'rgb(34, 197, 94)',    // green-400
      ]
    }
  }

  if (selectedChartType.value === 'bar') {
    return {
      ...baseProps,
      backgroundColor: 'rgb(59, 130, 246)' // blue-500
    }
  }

  return {
    ...baseProps,
    borderColor: 'rgb(59, 130, 246)', // blue-500
    backgroundColor: 'rgba(59, 130, 246, 0.1)', // blue-500 with opacity
    fill: true
  }
})

// Formatear moneda
function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

// Calcular porcentaje
function calculatePercentage(amount: number): string {
  if (totalAmount.value === 0) return '0'
  return ((amount / totalAmount.value) * 100).toFixed(1)
}

// Simular hover (en una implementación real, esto vendría de eventos de Chart.js)
function handleDataHover(index: number | null) {
  if (index === null || index < 0 || index >= props.data.length) {
    hoveredData.value = null
    emit('dataHover', null)
    return
  }

  const item = props.data[index]
  if (!item) {
    hoveredData.value = null
    emit('dataHover', null)
    return
  }
  
  const hoverData = {
    label: item.category,
    value: item.amount,
    percentage: parseFloat(calculatePercentage(item.amount))
  }
  
  hoveredData.value = hoverData
  emit('dataHover', hoverData)
}

// Watchers para emitir cambios
watch(selectedPeriod, (newPeriod) => {
  emit('periodChange', newPeriod)
})

watch(selectedChartType, (newType) => {
  emit('chartTypeChange', newType)
})

// Exponer métodos
defineExpose({
  handleDataHover
})
</script>

<style scoped>
.spending-chart {
  width: 100%;
}

.chart-container {
  min-height: 300px;
  max-height: 400px;
}

@media (max-width: 640px) {
  .chart-container {
    min-height: 250px;
  }
}

/* Iconos SVG inline para los botones */
button svg {
  display: inline-block;
}
</style>
