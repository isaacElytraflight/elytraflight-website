/**
 * Copy the Skillgrove shell to the profile URLs a static host can serve.
 *
 * elytraflight.com is a Render static site created in the dashboard. Routes in
 * render.yaml are not applied there (unknown paths return a plain-text 404,
 * and /CS180Proj0 is 200 rather than the 301 in render.yaml). public/serve.json
 * is only read by the local `serve` dev server.
 *
 * A directory index is served for that directory only. These copies make
 * /skilltree/profile/?u=<username> and /profile/?u=<username> return the app.
 * /profile/<username> is not a file. On this host it stays 404 until the
 * dashboard has a rewrite:
 *   Source /profile/*  Destination /profile/index.html  Action Rewrite
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const PROFILE_FALLBACKS = [
  'skilltree/profile/index.html',
  'profile/index.html',
]

/** Local files the shell loads with relative URLs. The published /skilltree/index.html keeps those relative URLs. Copies do not: a browser preload scan resolves them against the nested URL before the base tag runs, so /skilltree/profile/skilltree.js 404s. */
const RELATIVE_ASSETS = [
  'favicon.svg',
  'skilltree.css',
  'config.js',
  'supabase.min.js',
  'simcore.js',
  'migrate.js',
  'auth.js',
  'expr.js',
  'skilltree.js',
]

export function profileFallbackHtml(html) {
  let out = String(html)
  for (const name of RELATIVE_ASSETS) {
    out = out.replaceAll(`href="${name}"`, `href="/skilltree/${name}"`)
    out = out.replaceAll(`src="${name}"`, `src="/skilltree/${name}"`)
  }
  return out
}

export function emitProfileFallbacks(buildDir) {
  const source = path.join(buildDir, 'skilltree', 'index.html')
  if (!fs.existsSync(source) || !fs.statSync(source).isFile()) {
    throw new Error(`Skillgrove shell not found at ${source}`)
  }
  const html = profileFallbackHtml(fs.readFileSync(source, 'utf8'))
  const written = []
  for (const rel of PROFILE_FALLBACKS) {
    const dest = path.join(buildDir, rel)
    fs.mkdirSync(path.dirname(dest), { recursive: true })
    fs.writeFileSync(dest, html)
    written.push(dest)
  }
  return written
}

const invokedDirectly = process.argv[1]
  && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url))

if (invokedDirectly) {
  const buildDir = path.resolve(process.argv[2] || 'build')
  const written = emitProfileFallbacks(buildDir)
  for (const file of written) console.log(`profile fallback ${path.relative(buildDir, file)}`)
}
