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

/**
 * Point local src/href values at /skilltree/. The published shell keeps
 * relative URLs, which are correct at /skilltree/. Copies do not: the preload
 * scan resolves them against the nested page before the base tag runs.
 * Tag attributes only, so the base-href script is left alone.
 */
export function profileFallbackHtml(html) {
  return String(html).replace(/<(link|script|img|a)\b[^>]*>/gi, (tag) => tag.replace(
    /\b(href|src)="([^"]*)"/gi,
    (attr, key, value) => {
      if (!value || /^(?:https?:|\/\/|\/|#|data:|mailto:)/i.test(value)) return attr
      return `${key}="/skilltree/${value.replace(/^\.\//, '')}"`
    }
  ))
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
