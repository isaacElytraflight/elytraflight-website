/**
 * Profile URLs on a static host (Render), which serves files and directory
 * indexes and does not apply render.yaml or serve.json rewrites.
 *
 * Run from the repo root: node public/skilltree/tests/test-profile-fallbacks.mjs
 */
import assert from 'node:assert'
import fs from 'node:fs'
import http from 'node:http'
import os from 'node:os'
import path from 'node:path'
import vm from 'node:vm'
import { fileURLToPath } from 'node:url'
import { emitProfileFallbacks, profileFallbackHtml } from '../../../scripts/emit-profile-fallbacks.mjs'

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..')
const shellPath = path.join(repoRoot, 'public', 'skilltree', 'index.html')

let passed = 0
let failed = 0

function test(name, fn) {
  try {
    fn()
    console.log(`✓ ${name}`)
    passed++
  } catch (e) {
    console.log(`✗ ${name}`)
    console.error('  ', e && e.stack ? e.stack : e)
    failed++
  }
}

async function testAsync(name, fn) {
  try {
    await fn()
    console.log(`✓ ${name}`)
    passed++
  } catch (e) {
    console.log(`✗ ${name}`)
    console.error('  ', e && e.stack ? e.stack : e)
    failed++
  }
}

/** Same lookup the live static host uses: file, file.html, or directory index. */
function staticFile(root, urlPath) {
  const pathname = decodeURIComponent(urlPath.split('?')[0] || '/')
  if (pathname.includes('\0') || pathname.split('/').includes('..')) return null
  const rel = pathname.replace(/^\/+/, '')
  const exact = path.resolve(root, rel)
  const rootResolved = path.resolve(root)
  if (exact !== rootResolved && !exact.startsWith(rootResolved + path.sep)) return null
  const candidates = pathname.endsWith('/')
    ? [path.join(exact, 'index.html')]
    : [exact, exact + '.html', path.join(exact, 'index.html')]
  for (const file of candidates) {
    if (fs.existsSync(file) && fs.statSync(file).isFile()) return file
  }
  return null
}

function baseHrefFor(html, pathname) {
  const match = html.match(/<script>\s*([\s\S]*?)<\/script>/)
  assert.ok(match, 'shell has the base-href script')
  let written = ''
  vm.runInNewContext(match[1], {
    location: { pathname },
    document: { write(chunk) { written += String(chunk) } },
  })
  const href = written.match(/href="([^"]*)"/)
  return href ? href[1] : ''
}

function assetPath(html, pathname, relative) {
  const base = baseHrefFor(html, pathname)
  const documentUrl = new URL(pathname, 'https://www.elytraflight.com')
  const baseUrl = base ? new URL(base, 'https://www.elytraflight.com') : documentUrl
  return new URL(relative, baseUrl).pathname
}

function publishFixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'profile-fallbacks-'))
  fs.mkdirSync(path.join(root, 'skilltree'), { recursive: true })
  fs.copyFileSync(shellPath, path.join(root, 'skilltree', 'index.html'))
  fs.writeFileSync(path.join(root, 'skilltree', 'skilltree.js'), '/* skilltree */')
  fs.writeFileSync(path.join(root, 'skilltree', 'skilltree.css'), '/* css */')
  fs.writeFileSync(path.join(root, 'skilltree', 'favicon.svg'), '<svg xmlns="http://www.w3.org/2000/svg"/>')
  emitProfileFallbacks(root)
  return root
}

function listen(server) {
  return new Promise((resolve, reject) => {
    server.once('error', reject)
    server.listen(0, '127.0.0.1', () => resolve(server.address().port))
  })
}

console.log('\n=== Profile static fallbacks ===\n')

test('build copies the shell onto the two directory indexes with root-absolute assets', () => {
  const root = publishFixture()
  const shell = fs.readFileSync(path.join(root, 'skilltree', 'index.html'), 'utf8')
  const expected = profileFallbackHtml(shell)
  assert.notStrictEqual(expected, shell)
  assert.match(expected, /src="\/skilltree\/skilltree\.js"/)
  assert.match(expected, /href="\/skilltree\/skilltree\.css"/)
  assert.doesNotMatch(expected, /(?:src|href)="(?:favicon\.svg|skilltree\.css|config\.js|supabase\.min\.js|simcore\.js|migrate\.js|auth\.js|expr\.js|skilltree\.js)"/)
  assert.match(expected, /id="profilePage"/)
  for (const rel of ['skilltree/profile/index.html', 'profile/index.html']) {
    const file = path.join(root, rel)
    assert.ok(fs.existsSync(file), rel)
    assert.strictEqual(fs.readFileSync(file, 'utf8'), expected, rel)
  }
  assert.match(shell, /src="skilltree\.js"/, 'the /skilltree/ shell keeps relative URLs')
  fs.rmSync(root, { recursive: true, force: true })
})

test('a missing shell fails the build', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'profile-fallbacks-empty-'))
  assert.throws(() => emitProfileFallbacks(root), /Skillgrove shell not found/)
  fs.rmSync(root, { recursive: true, force: true })
})

test('nested profile URLs resolve relative assets back to /skilltree/', () => {
  const html = fs.readFileSync(shellPath, 'utf8')
  const paths = [
    '/skilltree/',
    '/skilltree',
    '/skilltree/profile/',
    '/skilltree/profile',
    '/profile/',
    '/profile',
    '/profile/test',
    '/profile/ada_1/',
  ]
  for (const pathname of paths) {
    for (const asset of ['skilltree.js', 'skilltree.css', 'favicon.svg']) {
      assert.strictEqual(
        assetPath(html, pathname, asset),
        '/skilltree/' + asset,
        pathname + ' ' + asset
      )
    }
  }
})

await testAsync('a static host serves both profile directory URLs and 404s /profile/<username>', async () => {
  const root = publishFixture()
  const server = http.createServer((req, res) => {
    const file = staticFile(root, req.url || '/')
    if (!file) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' })
      res.end('Not Found')
      return
    }
    const type = file.endsWith('.html') ? 'text/html; charset=utf-8'
      : file.endsWith('.js') ? 'text/javascript; charset=utf-8'
      : 'text/plain; charset=utf-8'
    res.writeHead(200, { 'content-type': type })
    fs.createReadStream(file).pipe(res)
  })
  const port = await listen(server)
  const origin = `http://127.0.0.1:${port}`
  try {
    const shell = fs.readFileSync(path.join(root, 'skilltree', 'profile', 'index.html'), 'utf8')
    for (const urlPath of [
      '/skilltree/profile/?u=test',
      '/skilltree/profile',
      '/skilltree/profile/',
      '/profile/?u=test',
      '/profile',
      '/profile/',
    ]) {
      const res = await fetch(origin + urlPath)
      assert.strictEqual(res.status, 200, urlPath)
      assert.match(res.headers.get('content-type') || '', /text\/html/)
      const body = await res.text()
      assert.strictEqual(body, shell, urlPath)
      assert.match(body, /id="profilePage"/)
      assert.match(body, /src="\/skilltree\/skilltree\.js"/)
    }

    const nestedJs = await fetch(origin + '/skilltree/profile/skilltree.js')
    assert.strictEqual(nestedJs.status, 404, 'the nested directory must not shadow /skilltree/skilltree.js')

    for (const asset of ['/skilltree/skilltree.js', '/skilltree/skilltree.css', '/skilltree/favicon.svg']) {
      const res = await fetch(origin + asset)
      assert.strictEqual(res.status, 200, asset)
    }

    const username = await fetch(origin + '/profile/test')
    assert.strictEqual(username.status, 404)
    assert.strictEqual(await username.text(), 'Not Found')
  } finally {
    await new Promise((resolve, reject) => server.close(err => err ? reject(err) : resolve()))
    fs.rmSync(root, { recursive: true, force: true })
  }
})

console.log(`\n${passed} passed, ${failed} failed\n`)
process.exit(failed > 0 ? 1 : 0)
