import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/campaigns': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/templates': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/contacts': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/lists': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/tags': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/segments': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/suppressions': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/onboarding': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/track': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
