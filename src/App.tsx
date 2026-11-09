import './styles/global.css'

const TREE_MARK = (
  <svg className="mark" width="40" height="40" viewBox="0 0 40 40" aria-hidden="true">
    <circle cx="20" cy="20" r="19" fill="#fff4d6" />
    <path d="M20 33V19" stroke="#2f9e6a" strokeWidth="3" strokeLinecap="round" />
    <circle cx="20" cy="13" r="6" fill="#ff7a59" />
    <circle cx="12" cy="21" r="5" fill="#ffc93c" />
    <circle cx="28" cy="21" r="5" fill="#22b8e6" />
    <circle cx="20" cy="26" r="4.5" fill="#7c6cff" />
  </svg>
)

type SampleTile = {
  tier: 0 | 1 | 2 | 3 | 4
  label: string
  fill: string
  color: string
}

const TREE_ROWS: SampleTile[][] = [
  [{ tier: 4, label: 'Mastered', fill: '100%', color: '#7c6cff' }],
  [
    { tier: 3, label: 'Level 2', fill: '80%', color: '#22b8e6' },
    { tier: 2, label: 'Level 1', fill: '55%', color: '#2ed47a' },
  ],
  [
    { tier: 1, label: 'Practiced', fill: '30%', color: '#ff9f43' },
    { tier: 0, label: 'Unpracticed', fill: '0%', color: '#4c8dff' },
    { tier: 1, label: 'Practiced', fill: '30%', color: '#ff6b6b' },
  ],
]

const FEATURES = [
  {
    title: 'A tree that fills in by tier',
    body: 'Skills sit in a prerequisite tree that grows upward from the foundations. Each tile fills with its chapter color as you climb: empty, then 30%, 55%, 80%, and full at Mastered.',
  },
  {
    title: 'Five tiers and spaced mastery challenges',
    body: 'The tiers are Unpracticed, Practiced, Level 1, Level 2, and Mastered. Round 1 is a practice quiz. Rounds 2–4 are mastery challenges: three questions, at least two correct to move up. The queue lists the least recently practiced skill first, and a miss never drops your tier.',
  },
  {
    title: 'Practice questions with explanations',
    body: 'After each question you see whether you were right, the correct answer, and a written explanation of why.',
  },
  {
    title: 'Read-first explainers',
    body: 'A skill with an explainer opens it from the skill panel. Before you have practiced that skill, the button says Read first.',
  },
  {
    title: 'Diagrams',
    body: 'Questions and explainers can include SVG figures. Each figure keeps a text alternative.',
  },
  {
    title: 'Sign in, and progress follows you',
    body: 'Sign in with an email magic link or Google. Progress stays on this device and, once you are signed in, syncs across devices. If both copies have a skill, the higher tier is kept.',
  },
  {
    title: 'Export and import',
    body: 'Settings can export a JSON backup and import it later, including on another device. Import can merge with what is already saved here, or replace it.',
  },
] as const

const COURSES: { title: string; body: string }[] = [
  {
    title: 'EE 105',
    body: 'Signals, semiconductor devices, and analog circuits.',
  },
  {
    title: 'ME 132',
    body: 'Feedback, dynamics, and control.',
  },
]

const PROJECTS = [
  {
    href: '/CS180Proj0/',
    kicker: 'Project 0',
    title: 'Becoming Friends with Your Camera',
  },
  {
    href: '/CS180Proj1/',
    kicker: 'Project 1',
    title: 'Colorizing the Prokudin-Gorskii collection',
  },
  {
    href: '/CS180Proj2/',
    kicker: 'Project 2',
    title: 'Fun with Filters and Frequencies',
  },
  {
    href: '/CS180Proj3/',
    kicker: 'Project 3',
    title: 'Fun with Flow Models',
  },
  {
    href: '/CS180Proj4A/',
    kicker: 'Project 4A',
    title: 'Image Warping and Mosaicing',
  },
] as const

function Tile({ tile }: { tile: SampleTile }) {
  return (
    <div
      className={`tile t${tile.tier}`}
      style={{ ['--c' as string]: tile.color, ['--fill' as string]: tile.fill }}
    >
      <span className="fill" />
      <span className="nm">{tile.label}</span>
      <span className="meta">
        <span className="pips">
          {[0, 1, 2, 3].map((i) => (
            <i key={i} className={tile.tier > i ? 'on' : undefined} />
          ))}
        </span>
        <span>{tile.fill === '0%' ? 'Empty' : tile.fill}</span>
      </span>
    </div>
  )
}

function App() {
  return (
    <>
      <a className="skip" href="#content">
        Skip to content
      </a>
      <header className="site-header">
        <a className="brand" href="#top">
          {TREE_MARK}
          <span>Elytraflight</span>
        </a>
        <nav className="nav" aria-label="Page">
          <a href="#features">Features</a>
          <a href="#courses">Courses</a>
          <a href="#projects">CS 180</a>
        </nav>
        <a className="btn hot" href="/skilltree/">
          Open Skillgrove
        </a>
      </header>

      <main id="content">
        <section className="hero" id="top" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">Elytraflight</p>
            <h1 id="hero-title">Master STEM skills, one node at a time.</h1>
            <p className="lede">
              Skillgrove is Elytraflight’s mastery-based learning site for undergraduate STEM.
              Practice a skill, climb its tier, and watch the tree fill in. EE 105 is one course on
              that tree.
            </p>
            <div className="hero-actions">
              <a className="btn hot lg" href="/skilltree/">
                Open Skillgrove
              </a>
              <a className="btn lg" href="#features">
                See what it includes
              </a>
            </div>
          </div>
          <figure className="tree-card">
            <div className="grove" aria-hidden="true">
              {TREE_ROWS.map((row) => (
                <div className="grove-row" key={row.map((tile) => tile.label + tile.color).join('-')}>
                  {row.map((tile) => (
                    <Tile key={tile.label + tile.color} tile={tile} />
                  ))}
                </div>
              ))}
            </div>
            <figcaption>
              Tiles fill with their chapter color as you climb. Four pips mark the tier, from
              Unpracticed to Mastered.
            </figcaption>
          </figure>
        </section>

        <section id="features" aria-labelledby="features-title">
          <div className="section-head">
            <h2 id="features-title">What Skillgrove includes</h2>
            <p>These are the pieces already in the app at /skilltree/.</p>
          </div>
          <ul className="feature-grid">
            {FEATURES.map((feature) => (
              <li key={feature.title}>
                <h3>{feature.title}</h3>
                <p>{feature.body}</p>
              </li>
            ))}
          </ul>
        </section>

        <section id="courses" aria-labelledby="courses-title">
          <div className="section-head">
            <h2 id="courses-title">Courses on the tree</h2>
            <p>
              Skillgrove is built for STEM courses in general. Two courses are available now. Open
              Skillgrove and choose either one.
            </p>
          </div>
          <ul className="course-grid">
            {COURSES.map((course) => (
              <li key={course.title}>
                <h3>{course.title}</h3>
                <p>{course.body}</p>
                <a href="/skilltree/">Open {course.title} in Skillgrove</a>
              </li>
            ))}
          </ul>
          <p className="note">Some skills do not have questions yet and show as coming soon.</p>
        </section>

        <section id="projects" aria-labelledby="projects-title">
          <div className="section-head">
            <h2 id="projects-title">Isaac’s CS 180 projects</h2>
            <p>Computational photography write-ups from CS 180. Each page stays at its own address.</p>
          </div>
          <ul className="project-grid">
            {PROJECTS.map((project) => (
              <li key={project.href}>
                <a href={project.href}>
                  <span className="kicker">{project.kicker}</span>
                  <span className="project-title">{project.title}</span>
                </a>
              </li>
            ))}
          </ul>
        </section>
      </main>

      <footer className="site-footer">
        <p>
          <strong>Elytraflight</strong> · home of{' '}
          <a href="/skilltree/">Skillgrove</a>
        </p>
      </footer>
    </>
  )
}

export default App
