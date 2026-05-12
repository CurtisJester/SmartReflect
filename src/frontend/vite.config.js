import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, path.resolve(__dirname, '../..'), '')
  return {
    plugins: [react()],
    define: {
      'import.meta.env.FASTAPI_CLOUD_URL': JSON.stringify(env.FASTAPI_CLOUD_URL),
    },
  }
})
