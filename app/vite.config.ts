import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [react()],
  // Published at https://www.motleytech.net/math/ (see publish.sh); / for the dev server.
  base: command === 'build' ? '/math/' : '/',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
}))
