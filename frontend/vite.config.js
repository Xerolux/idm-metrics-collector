// Xerolux 2026
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [vue()],
  base: '/static/',
  build: {
    outDir: '../idm_logger/static',
    emptyOutDir: true,
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            {
              name: 'vendor',
              test: /[\\/]node_modules[\\/](vue|vue-router|pinia|axios)[\\/]/,
              priority: 30
            },
            {
              name: 'chartjs',
              test: /[\\/]node_modules[\\/](chart\.js|vue-chartjs|chartjs-adapter-date-fns|chartjs-plugin-zoom|chartjs-plugin-annotation)[\\/]/,
              priority: 20
            },
            {
              name: 'primevue',
              test: /[\\/]node_modules[\\/](primevue|@primevue|@primeuix)[\\/]/,
              priority: 10
            }
          ]
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
