import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8081',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1/, '/api/v1'),
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.error('代理请求错误:', err)
          })
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('代理请求:', req.method, req.url)
          })
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('代理响应:', proxyRes.statusCode, req.url)
          })
        }
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
