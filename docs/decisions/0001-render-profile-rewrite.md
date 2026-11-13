# 1. Profile URLs on the Render static site

Date: 2026-11-13
Status: accepted

## Context

elytraflight.com is a Render static site created in the dashboard. A dashboard-created static site serves files and directory indexes. It does not apply the routes in `render.yaml`. Unknown paths return a plain-text 404. `public/serve.json` is read only by the local `serve` dev server.

Profile links need the skill-tree shell at `/skilltree/profile/` and `/profile/`. A path with an extra segment, such as `/profile/<username>`, is not a file.

## Decision

The production build copies the skill-tree shell to `profile/index.html` and `skilltree/profile/index.html`. `scripts/emit-profile-fallbacks.mjs` rewrites relative asset URLs in those copies to absolute `/skilltree/...` paths. The preload scan resolves a relative URL against the nested page before the base tag runs, so a relative URL in the copy would 404.

`render.yaml` still records the rewrites, including `/profile/*` to `/profile/index.html`. Those routes apply only if the service is created from the Blueprint. They are not what the live site uses today.

## Consequences

`/skilltree/profile/?u=<username>` and `/profile/?u=<username>` work from the copied files. `/profile/<username>` stays 404 on the live host until the Render dashboard has a rewrite: source `/profile/*`, destination `/profile/index.html`, action Rewrite. The same gap exists for `/skilltree/profile/<username>` until that dashboard rewrite exists. Isaac confirms those dashboard rewrites. Do not assume `render.yaml` or `serve.json` has already done it.

`npm run build` emits the copies. `node public/skilltree/tests/test-profile-fallbacks.mjs` checks them.
