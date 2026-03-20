import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Filler
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import zoomPlugin from 'chartjs-plugin-zoom'
import annotationPlugin from 'chartjs-plugin-annotation'
import { MatrixController, MatrixElement } from 'chartjs-chart-matrix'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler,
  zoomPlugin,
  annotationPlugin,
  MatrixController,
  MatrixElement
)

export const isDarkMode = () => document.documentElement.classList.contains('my-app-dark')

export const getChartColors = (isDark = false) => ({
  background: isDark ? 'rgba(31, 41, 55, 0.95)' : 'rgba(255, 255, 255, 0.95)',
  title: isDark ? '#f3f4f6' : '#1f2937',
  body: isDark ? '#d1d5db' : '#4b5563',
  border: isDark ? '#374151' : '#e5e7eb',
  grid: isDark ? '#374151' : '#f0f0f0',
  ticks: isDark ? '#9ca3af' : '#666'
})

export const createBaseOptions = (isDual = false, isDark = false) => {
  const colors = getChartColors(isDark)

  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: colors.background,
        titleColor: colors.title,
        bodyColor: colors.body,
        borderColor: colors.border,
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        boxPadding: 4,
        usePointStyle: true
      }
    },
    scales: {
      x: {
        display: true,
        type: 'time',
        time: {
          tooltipFormat: 'dd.MM.yyyy HH:mm',
          displayFormats: { hour: 'HH:mm', day: 'dd.MM' }
        },
        grid: { display: true, color: colors.grid },
        ticks: { maxTicksLimit: 8, maxRotation: 0, color: colors.ticks, font: { size: 10 } }
      },
      y: {
        display: true,
        position: 'left',
        grid: { color: colors.grid },
        ticks: { color: colors.ticks, font: { size: 10 } }
      },
      ...(isDual ? {
        y1: {
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: colors.ticks, font: { size: 10 } }
        }
      } : {})
    },
    elements: {
      point: { radius: 2, hitRadius: 10, hoverRadius: 4 },
      line: { tension: 0.4, borderWidth: 2 }
    }
  }
}

export default ChartJS
