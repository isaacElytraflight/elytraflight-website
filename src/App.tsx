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
    title: 'Watch your progress fill in',
    body: 'Skills sit on a colorful tree, with the basics along the bottom and later skills above them. Each one fills with color as you get better, until it is fully mastered.',
  },
  {
    title: 'Climb in steps, then come back',
    body: 'You move through five steps: Unpracticed, Practiced, Level 1, Level 2, and Mastered. A first practice gets you started. Later, a short challenge checks that the skill stuck, and the ones you have not visited in a while come back first. Missing never takes away a step you already earned.',
  },
  {
    title: 'Try a question, then see why',
    body: 'After you answer, you see whether you were right, the correct answer, and a plain explanation. You learn from the try, not only from a score.',
  },
  {
    title: 'Read the idea first',
    body: 'Before you practice a new skill, you can open a short explanation. The button says Read first, so you can understand the idea and then try the questions.',
  },
  {
    title: 'Pictures beside the words',
    body: 'Questions and explanations often include a diagram, so the idea is easier to picture.',
  },
  {
    title: 'Pick up where you left off',
    body: 'Sign in with your email or with Google. Your place in the tree stays on this device, and it is waiting when you sign in on another one. If you have gone further on one of them, that further progress is what you keep.',
  },
  {
    title: 'Keep a copy of your progress',
    body: 'You can save your progress and open it again later, on this device or another.',
  },
] as const

const COURSES = [
  {
    title: 'Berkeley EE 105',
    body: 'Signals, semiconductor devices, and analog circuits.',
  },
  {
    title: 'Berkeley ME 132',
    body: 'Feedback, dynamics, and control.',
  },
] as const

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
            <h1 id="hero-title">Master one STEM skill at a time.</h1>
            <p className="lede">
              Skillgrove is Elytraflight’s learning site for undergraduate STEM. Practice until a
              skill feels solid, watch it fill in with color, and come back so it stays with you.
              Berkeley EE 105 is one of the courses you can study.
            </p>
            <div className="hero-actions">
              <a className="btn hot lg" href="/skilltree/">
                Open Skillgrove
              </a>
              <a className="btn lg" href="#features">
                See how it helps
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
              Color fills in as a skill goes from new to mastered.
            </figcaption>
          </figure>
        </section>

        <section id="features" aria-labelledby="features-title">
          <div className="section-head">
            <h2 id="features-title">How learning feels</h2>
            <p>A path you can see, practice that comes back, and progress that stays with you.</p>
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
            <h2 id="courses-title">Courses to explore</h2>
            <p>
              Skillgrove is for undergraduate STEM in general. Open it and choose a course. These
              two are ready now.
            </p>
          </div>
          <ul className="course-grid">
            {COURSES.map((course) => (
              <li key={course.title}>
                <h3>{course.title}</h3>
                <p>{course.body}</p>
              </li>
            ))}
          </ul>
        </section>

        <section id="projects" aria-labelledby="projects-title">
          <div className="section-head">
            <h2 id="projects-title">Isaac’s CS 180 projects</h2>
            <p>Computational photography projects from CS 180.</p>
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
