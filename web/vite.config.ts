import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: true,
    // No dev proxy: the real API client (web/src/api/cardeep.ts) calls VITE_API_BASE
    // (:8090) directly. The previous '/api' proxy target was orphaned — nothing in
    // this repo ever served that port (docker-compose.yml defines cardeep-pg/api/
    // autopilot only); it only fed the now-quarantined report/dossier hooks.
    // Removed 02-history-reports F0 (2026-07-18).
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['recharts'],
          dnd: ['@dnd-kit/core', '@dnd-kit/sortable', '@dnd-kit/utilities'],
          three: ['three', '@react-three/fiber', '@react-three/drei'],
        },
      },
    },
  },
})
