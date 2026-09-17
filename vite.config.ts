import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

type DevRequest = { url?: string }

/** Serve public/CS180ProjN/index.html for /CS180ProjN and /CS180ProjN/ in dev. */
function cs180StaticPages(): Plugin {
  return {
    name: 'cs180-static-pages',
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        const request = req as DevRequest
        const url = request.url ?? ''
        const path = url.split('?')[0] ?? ''
        const match = path.match(/^\/CS180Proj(\d+)\/?$/i)
        if (match) {
          const query = url.includes('?') ? url.slice(url.indexOf('?')) : ''
          request.url = `/CS180Proj${match[1]}/index.html${query}`
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
