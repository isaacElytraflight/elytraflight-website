# Elytraflight

A 3D portfolio website where visitors fly through the clouds to explore portfolio sections on floating islands.

**Live:** [elytraflight.com](https://elytraflight.com)

## Features

- Sunset skyscape with volumetric clouds and fog
- Three floating islands: About, Projects, Contact
- Free-flight navigation with keyboard (desktop) or touch controls (mobile)
- Proximity-based content panels when you reach each island

## Controls

**Desktop**
- Click to start flying (pointer lock)
- `WASD` — move
- `Space` / `Shift` — ascend / descend
- Mouse — look around
- `Esc` — release pointer lock

**Mobile**
- Tap **Fly** to start
- Left half of screen — move
- Right half — drag to look

## Development

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Editing Content

Island positions and copy live in [`src/data/sections.ts`](src/data/sections.ts). Update text, links, and project cards there without touching 3D code.

## Deployment

The site builds to static files and deploys to Render via [`render.yaml`](render.yaml):

```bash
npm run build
```

Render serves the `dist/` folder. Push to `main` on GitHub to trigger auto-deploy.
