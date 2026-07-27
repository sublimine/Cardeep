import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    allowedHosts: true,
    // 08-forum-community F3: restored, pointing at the REAL live API this time (unlike the
    // '/api' proxy 02-history-reports F0 removed as orphaned — that one fed the now-quarantined
    // report/dossier hooks against a port nothing served). web/src/api/client.ts (used by
    // AuthContext.tsx/CRM hooks/dealer_ops — NOT cardeep.ts, which calls VITE_API_BASE
    // directly) hardcodes relative fetches to '/api/v1/*'. Without this proxy, the Vite dev
    // server's SPA fallback answers every '/api/v1/*' request with index.html (200, text/html)
    // instead of a 404 or the real JSON — apiRequest()'s res.json() then throws on the HTML
    // body, so login/register/every CRM call silently breaks in a real browser dev session.
    // Verified live: curl http://localhost:5173/api/v1/auth/me returned the Vite SPA shell
    // before this fix. Declared as a known gap by 06-unified-crm-chat F1-F6 and
    // 07-marketing F4 ("bloquea E2E autenticado de CUALQUIER página, declarado para AUTH-0")
    // and left unfixed by AUTH-0 (which only verified login via curl against :8090 directly,
    // not through the Vite dev server) — fixed here because 08-forum-community F3's own
    // verification criterion ("E2E publica->ve matches->...") needs a real authenticated
    // browser session to mean anything, and the fix benefits every other authenticated page
    // in the platform at zero cost (dev-only; `build` is untouched, `web/src/api/cardeep.ts`
    // is untouched).
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:8090',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1/, ''),
      },
    },
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
