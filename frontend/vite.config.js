import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/agent': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/metrics': 'http://localhost:8000',
      '/sms': 'http://localhost:8000',
      '/voice': 'http://localhost:8000',
      '/static': 'http://localhost:8000'
    }
  }
})
