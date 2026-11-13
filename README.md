# Elytraflight

Elytraflight is home to [Elytraflight's Skill Tree](https://elytraflight.com/skilltree/), a general STEM learning site. Master STEM skills, one node at a time.

**Live:** [elytraflight.com](https://elytraflight.com)

The home page introduces Elytraflight's Skill Tree and links to Isaac’s CS 180 project pages. The skill tree and those project pages are standalone files in `public/` and are copied into the build as-is:

- [`/skilltree/`](public/skilltree/)
- [`/CS180Proj0/`](public/CS180Proj0/)
- [`/CS180Proj1/`](public/CS180Proj1/)
- [`/CS180Proj2/`](public/CS180Proj2/)
- [`/CS180Proj3/`](public/CS180Proj3/)
- [`/CS180Proj4A/`](public/CS180Proj4A/)

## Development

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Deployment

The site builds to static files and deploys to Render via [`render.yaml`](render.yaml):

```bash
npm run build
```

Render serves the `build/` folder. Push to `main` on GitHub to trigger auto-deploy.

### Render dashboard settings

If deploy fails with "Empty build command" or "Publish directory does not exist", set these on your **Static Site** in the Render dashboard:

| Setting | Value |
|---|---|
| **Build Command** | `npm run build` |
| **Publish Directory** | `build` |

Use `build` without a leading slash. The `render.yaml` in this repo is only applied if the service is created from a Blueprint; manually created services need the values above.
