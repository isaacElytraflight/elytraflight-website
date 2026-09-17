import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

/** Serve public/CS180ProjN/index.html for /CS180ProjN and /CS180ProjN/ in dev. */
function cs180StaticPages(): Plugin {
  return {
    name: 'cs180-static-pages',
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        const path = req.url?.split('?')[0] ?? ''
        const match = path.match(/^\/CS180Proj(\d+)\/?$/i)
        if (match) {
          const query = req.url?.includes('?') ? req.url.slice(req.url.indexOf('?')) : ''
          req.url = `/CS180Proj${match[1]}/index.html${query}`
        }
        next()
      })
    },
  }
}

export default defineConfig({
  plugins: [cs180StaticPages(), react()],
  build: {
    outDir: 'build',
  },
})
