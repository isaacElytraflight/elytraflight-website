# Skillgrove — Master STEM Skills

A mastery-based skill tree for undergraduate STEM courses, served at `/skilltree/` on elytraflight.com.

Skillgrove organizes skills into prerequisite trees where you climb from Unpracticed to Mastered through quizzes. Skills are grouped into courses and chapters via a flexible "collections" system that supports multiple courses, cross-university content sharing, and nested organization.

## Structure

```
public/skilltree/
├── index.html              # Main HTML (lightweight, loads external assets)
├── skilltree.css           # All styles (~24 KB)
├── config.js               # Supabase URL & public key, auth flags
├── supabase.min.js         # Vendored supabase-js v2 (~218 KB)
├── simcore.js              # Learning plan simulator module (~4 KB)
├── auth.js                 # Auth & sync module (sign-in, merge, sync)
├── skilltree.js            # Main app with lazy loading (~65 KB)
├── manifest.json           # Content hashes for cache control
├── skills.<hash>.json      # Skill graph + metadata (~30 KB, loaded at startup)
├── collections.<hash>.json # Course/chapter hierarchy (loaded at startup)
├── banks/                  # Question banks, loaded lazily on quiz start
│   └── ... (106 banks)
└── explainers/             # Skill explainers, loaded lazily ("Read first")
    └── ... (106 explainers)
```

## How It Works

1. **Startup**: Loads `manifest.json` → `skills.<hash>.json` (graph data, ~25 KB)
2. **Quiz start**: Lazy-loads the specific `banks/<skill>.<hash>.json` (15-50 KB each)
3. **Caching**: Content-hashed filenames ensure browsers fetch fresh data after updates

KaTeX (math rendering) is loaded from CDN for smaller initial bundle.

## Building / Updating

Source files are in `/skilltree/` (banks, skills graph) and `/tools/skilltree-content/` (generators).

To rebuild the data files after editing question banks:

```bash
python3 tools/skilltree-content/build.py
```

This regenerates:
- `public/skilltree/skills.<hash>.json`
- `public/skilltree/banks/*.json`
- `public/skilltree/manifest.json`

### Adding/Editing Question Banks

1. Edit or create JSON files in `/skilltree/bank/` following the schema:
   ```json
   {
     "skill_id": "bode",
     "version": 1,
     "questions": [
       {
         "id": "bode-r1-q1",
         "round": 1,
         "type": "mc",
         "prompt": "Question text with \\( LaTeX \\)",
         "options": ["A", "B", "C", "D"],
         "correct_index": 0,
         "explanation": "Why A is correct"
       }
     ]
   }
   ```

2. Run the build script:
   ```bash
   python3 tools/skilltree-content/build.py
   ```

3. Commit the updated files in `public/skilltree/`

### Adding Skills

Edit `/skilltree/ee105_skills_draft.json` to add skills to the graph, then rebuild.

## Collections (Courses & Chapters)

Skills are organized into a hierarchy of "boxes" (courses, chapters, units) via `skilltree/collections.json`. A skill can belong to multiple boxes—useful for cross-listed courses or shared foundations.

### collections.json Schema

```json
{
  "version": 1,
  "boxes": [
    {
      "id": "ee105-ucb",
      "title": "EE 105 (UC Berkeley)",
      "kind": "course",
      "institution": "UC Berkeley",
      "term_or_version": "Fall 2022 (Niknejad Reader)",
      "children": ["ee105-ch1", "ee105-ch2"],
      "skills": []
    },
    {
      "id": "ee105-ch1",
      "title": "Chapter 1: Linear Time-Invariant Systems",
      "kind": "chapter",
      "color_index": 1,
      "children": [],
      "skills": ["lti-def", "rc-lpf", "cx-exp"]
    }
  ]
}
```

### Adding a New Course

1. Create a course box with `kind: "course"` and list its chapter children
2. Create chapter boxes with `kind: "chapter"` and list their skills
3. Skills stay in `ee105_skills_draft.json`—boxes just reference them by ID
4. A skill can appear in multiple boxes (e.g., "phasors" in both EE 105 and Physics 7B)
5. Run `python3 tools/skilltree-content/build.py` to regenerate

### Adding a Nested Box (Unit within Chapter)

Boxes can nest arbitrarily. Create a box with the parent chapter's ID in its `children`, then list the unit's skills:

```json
{
  "id": "ee105-ch1-lti",
  "title": "LTI Fundamentals",
  "kind": "unit",
  "children": [],
  "skills": ["lti-def", "sinusoid-resp"]
}
```

Then add `"ee105-ch1-lti"` to the parent chapter's `children` array.

## localStorage Keys

Progress is stored per web origin. The app uses these localStorage keys:

- `skilltree.progress.v1` — User's tier progress per skill
- `skilltree.layout.v1` — UI preference (tree vs grouped view)
- `skilltree.timing.v1` — Quiz timing samples for learning plan estimates

**Migration note**: When moving from the old single-file version, users should:
1. Export their progress from the old file (Export button)
2. Import it on the new site (Import button)

## Development

The app is plain JavaScript with no build step. Edit the files directly:

- `index.html` — Page structure
- `skilltree.css` — Styles
- `simcore.js` — Learning plan simulation (also used by tests)
- `skilltree.js` — Main application logic

### Testing

Tests are in `public/skilltree/tests/`. They include:

- **Unit tests** for merge functions (`test-merge.js`)
- **Unit tests** for retired-id progress migration (`test-migrate.js`)
- **Content integrity** for the skill graph, banks, and collections (`test-content.js`)
- **UI tests** using Puppeteer (`test.js`)

```bash
cd public/skilltree/tests
npm install

# Unit tests (no server needed)
node test-merge.js
node test-migrate.js
node test-content.js

# UI tests (needs local server)
# Start a server from repo root first:
npx serve public -l 5000 &

# Run UI tests pointing to the server:
SKILLTREE_URL=http://localhost:5000/skilltree/ node test.js
```

UI tests mock Supabase so no network calls are made.

## File Sizes

| Resource | Size | When Loaded |
|----------|------|-------------|
| index.html | ~3 KB | Initial |
| skilltree.css | ~22 KB | Initial |
| config.js | ~0.5 KB | Initial |
| supabase.min.js | ~218 KB | Initial |
| auth.js | ~10 KB | Initial |
| KaTeX CSS (CDN) | ~24 KB | Initial |
| KaTeX JS (CDN) | ~290 KB | Initial |
| simcore.js | ~4 KB | Initial |
| skilltree.js | ~60 KB | Initial |
| skills.json | ~25 KB | Initial |
| **Initial total** | **~660 KB** | |
| Each bank JSON | 15-50 KB | On quiz start |

## Supabase Sync (Optional)

Users can optionally sign in to sync progress across devices via Supabase.

### Supabase Project Setup

1. **Create the `progress` table** in your Supabase project:

   ```sql
   CREATE TABLE public.progress (
     user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
     data JSONB NOT NULL DEFAULT '{}',
     updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
   );

   ALTER TABLE public.progress ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Users can read own progress"
     ON public.progress FOR SELECT
     USING (auth.uid() = user_id);

   CREATE POLICY "Users can insert own progress"
     ON public.progress FOR INSERT
     WITH CHECK (auth.uid() = user_id);

   CREATE POLICY "Users can update own progress"
     ON public.progress FOR UPDATE
     USING (auth.uid() = user_id);
   ```

2. **Configure Auth URLs** in Supabase Dashboard → Authentication → URL Configuration:

   | Setting | Value |
   |---------|-------|
   | Site URL | `https://elytraflight.com` |
   | Redirect URLs | `https://elytraflight.com/skilltree/` |

   For local development, also add:
   - `http://localhost:5173/skilltree/`
   - `http://localhost:5000/skilltree/`

3. **Enable Email Auth** (enabled by default):
   - Dashboard → Authentication → Providers → Email
   - Enable "Magic Link" sign-in

4. **Enable Google OAuth (optional)**:
   - Dashboard → Authentication → Providers → Google
   - Configure OAuth credentials from Google Cloud Console
   - Set `googleEnabled: true` in `config.js`

### Configuration

The app reads Supabase config from `config.js`:

```javascript
window.SKILLTREE_CONFIG = {
  supabase: {
    url: 'https://your-project.supabase.co',
    anonKey: 'your-anon-key'
  },
  auth: {
    googleEnabled: false,  // Set true to show Google sign-in button
    redirectUrl: 'https://elytraflight.com/skilltree/'
  }
};
```

**Security**: Only the anon (public) key is used. Never commit secret keys.

### How Sync Works

- **localStorage stays primary** for offline-first experience
- On sign-in, remote and local progress are merged (higher tier wins, history is union-deduped)
- After each localStorage save, changes are synced to Supabase (debounced 2s)
- Signed-out users work exactly as before (localStorage only)

## Deploy

The site auto-deploys from `main` via Render. The `public/skilltree/` folder is copied to `build/skilltree/` during Vite build and served statically.
