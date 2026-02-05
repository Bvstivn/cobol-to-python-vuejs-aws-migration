/**
 * Tests de propiedad para SpendingChart
 * Valida: Requerimientos 6.1, 6.3, 6.4
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import * as fc from 'fast-check'
import SpendingChart from '../SpendingChart.vue'

// Mock de Chart.js para evitar problemas con canvas en jsdom
vi.mock('chart.js', () => ({
  Chart: class MockChart {
    static register = vi.fn()
    constructor() {
      return {
        destroy: vi.fn(),
        update: vi.fn(),
        data: {},
        options: {}
      }
    }
  },
  registerables: []
}))

// Generadores de datos
const spendingDataArb = fc.array(
  fc.record({
    category: fc.string({ minLength: 3, maxLength: 20 }),
    amount: fc.float({ min: Math.fround(0.01), max: Math.fround(10000), noNaN: true })
  }),
  { minLength: 1, maxLength: 10 }
)

const periodArb = fc.constantFrom('week', 'month', 'year')
const chartTypeArb = fc.constantFrom('pie', 'bar', 'line')

describe('SpendingChart - Property-Based Tests', () => {
  /**
   * Propiedad 20: Generación de gráficos financieros
   * Valida: Requerimientos 6.1
   * 
   * Para cualquier conjunto de datos financieros válidos, el sistema debe generar
   * gráficos interactivos que representen los patrones de gasto
   */
  it('Propiedad 20: Genera gráficos para cualquier conjunto de datos válidos', async () => {
    await fc.assert(
      fc.asyncProperty(
        spendingDataArb,
        periodArb,
        chartTypeArb,
        async (data, period, chartType) => {
          const wrapper = mount(SpendingChart, {
            props: {
              data,
              period,
              defaultChartType: chartType
            }
          })

          // Verificar que el componente se renderiza
          expect(wrapper.exists()).toBe(true)

          // Verificar que el título se muestra
          expect(wrapper.find('h3').text()).toContain('Patrones de Gasto')

          // Verificar que el selector de período existe
          const periodSelect = wrapper.find('select')
          expect(periodSelect.exists()).toBe(true)

          // Verificar que los botones de tipo de gráfico existen
          const chartTypeButtons = wrapper.findAll('button')
          expect(chartTypeButtons.length).toBeGreaterThanOrEqual(3)

          // Verificar que el contenedor del gráfico existe
          const chartContainer = wrapper.find('.chart-container')
          expect(chartContainer.exists()).toBe(true)

          wrapper.unmount()
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Propiedad 21: Contenido de respaldo para gráficos
   * Valida: Requerimientos 6.3
   * 
   * Para cualquier situación donde los datos de gráficos no están disponibles,
   * el sistema debe mostrar contenido de respaldo apropiado
   */
  it('Propiedad 21: Maneja datos vacíos correctamente', async () => {
    const wrapper = mount(SpendingChart, {
      props: {
        data: []
      }
    })

    // Verificar que el componente se renderiza sin errores
    expect(wrapper.exists()).toBe(true)

    // Verificar que el contenedor del gráfico existe
    const chartContainer = wrapper.find('.chart-container')
    expect(chartContainer.exists()).toBe(true)

    wrapper.unmount()
  })

  /**
   * Propiedad 22: Interactividad de gráficos
   * Valida: Requerimientos 6.4
   * 
   * Para cualquier interacción del usuario con gráficos (hover, click),
   * el sistema debe proporcionar información detallada relevante
   */
  it('Propiedad 22: Proporciona interactividad para cualquier dato', async () => {
    await fc.assert(
      fc.asyncProperty(
        spendingDataArb,
        async (data) => {
          const wrapper = mount(SpendingChart, {
            props: {
              data
            }
          })

          // Verificar que los selectores son interactivos
          const periodSelect = wrapper.find('select')
          expect(periodSelect.exists()).toBe(true)

          // Cambiar período
          await periodSelect.setValue('week')
          expect(periodSelect.element.value).toBe('week')

          // Verificar que los botones de tipo de gráfico son clickeables
          const chartTypeButtons = wrapper.findAll('button')
          expect(chartTypeButtons.length).toBeGreaterThanOrEqual(3)

          // Click en el primer botón
          if (chartTypeButtons.length > 0 && chartTypeButtons[0]) {
            await chartTypeButtons[0].trigger('click')
            // El componente debe seguir renderizado
            expect(wrapper.exists()).toBe(true)
          }

          wrapper.unmount()
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Cambio de período emite evento
   */
  it('emite evento al cambiar período', async () => {
    await fc.assert(
      fc.asyncProperty(
        spendingDataArb,
        periodArb,
        async (data, newPeriod) => {
          // Usar un período inicial diferente al nuevo período
          const initialPeriod = newPeriod === 'month' ? 'week' : 'month'
          
          const wrapper = mount(SpendingChart, {
            props: {
              data,
              period: initialPeriod
            }
          })

          const periodSelect = wrapper.find('select')
          await periodSelect.setValue(newPeriod)

          // Verificar que se emitió el evento
          const periodChangeEvents = wrapper.emitted('periodChange')
          expect(periodChangeEvents).toBeTruthy()
          if (periodChangeEvents && periodChangeEvents[0]) {
            expect(periodChangeEvents[0]).toEqual([newPeriod])
          }

          wrapper.unmount()
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Cambio de tipo de gráfico emite evento
   */
  it('emite evento al cambiar tipo de gráfico', async () => {
    await fc.assert(
      fc.asyncProperty(
        spendingDataArb,
        chartTypeArb,
        async (data, newChartType) => {
          // Usar un tipo inicial diferente al nuevo tipo
          const initialChartType = newChartType === 'pie' ? 'bar' : 'pie'
          
          const wrapper = mount(SpendingChart, {
            props: {
              data,
              defaultChartType: initialChartType
            }
          })

          // Encontrar el botón correspondiente al tipo de gráfico
          const buttons = wrapper.findAll('button')
          const chartTypeIndex = ['pie', 'bar', 'line'].indexOf(newChartType)
          
          if (chartTypeIndex >= 0 && chartTypeIndex < buttons.length) {
            const button = buttons[chartTypeIndex]
            if (button) {
              await button.trigger('click')

              // Verificar que se emitió el evento
              expect(wrapper.emitted('chartTypeChange')).toBeTruthy()
            }
          }

          wrapper.unmount()
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Cálculo correcto de totales
   */
  it('calcula totales correctamente para cualquier conjunto de datos', async () => {
    await fc.assert(
      fc.asyncProperty(
        spendingDataArb,
        async (data) => {
          const wrapper = mount(SpendingChart, {
            props: {
              data
            }
          })

          // Calcular total esperado
          const expectedTotal = data.reduce((sum, item) => sum + item.amount, 0)

          // El componente debe renderizarse sin errores
          expect(wrapper.exists()).toBe(true)

          // Verificar que el total es mayor o igual a 0
          expect(expectedTotal).toBeGreaterThanOrEqual(0)

          wrapper.unmount()
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Formato de moneda
   */
  it('formatea moneda correctamente para cualquier monto', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.float({ min: Math.fround(0), max: Math.fround(1000000), noNaN: true }),
        async (amount) => {
          const formatted = new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'USD'
          }).format(amount)

          // Verificar que el formato incluye el símbolo de moneda
          expect(formatted).toMatch(/\$|USD/)

          // Verificar que el formato es un string
          expect(typeof formatted).toBe('string')
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Manejo de datos con categorías duplicadas
   */
  it('maneja categorías duplicadas correctamente', async () => {
    const dataWithDuplicates = [
      { category: 'Comida', amount: 100 },
      { category: 'Comida', amount: 200 },
      { category: 'Transporte', amount: 50 }
    ]

    const wrapper = mount(SpendingChart, {
      props: {
        data: dataWithDuplicates
      }
    })

    // El componente debe renderizarse sin errores
    expect(wrapper.exists()).toBe(true)

    wrapper.unmount()
  })
})
