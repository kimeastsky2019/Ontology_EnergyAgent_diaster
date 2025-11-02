import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0', // 외부 접근 허용
    allowedHosts: [
      'damcp.gngmeta.com',
      'localhost',
      '127.0.0.1',
      '.gngmeta.com', // 모든 gngmeta.com 서브도메인 허용
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
  },
  // SPA를 위한 history API fallback 설정 (프로덕션 빌드 시)
  preview: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: [
      'damcp.gngmeta.com',
      'localhost',
      '127.0.0.1',
      '.gngmeta.com', // 모든 gngmeta.com 서브도메인 허용
    ],
  },
})




