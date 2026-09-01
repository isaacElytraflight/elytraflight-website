export type SectionLink = {
  label: string
  href: string
}

export type Project = {
  title: string
  description: string
  href?: string
}

export type Section = {
  id: 'about' | 'projects' | 'contact'
  title: string
  position: [number, number, number]
  body: string
  links?: SectionLink[]
  projects?: Project[]
}

export const PROXIMITY_RADIUS = 8

export const sections: Section[] = [
  {
    id: 'about',
    title: 'About',
    position: [0, 12, -30],
    body: "Hi, I'm Isaac — a developer who loves building immersive experiences. This site is my portfolio, reimagined as an elytra flight through the clouds. Fly to each island to learn more about me and my work.",
    links: [
      { label: 'GitHub', href: 'https://github.com/isaacElytraflight' },
    ],
  },
  {
    id: 'projects',
    title: 'Projects',
    position: [-35, 14, 10],
    body: 'A few things I have been working on. More coming soon.',
    projects: [
      {
        title: 'Elytraflight Website',
        description: 'This very site — a 3D cloud-flight portfolio built with React Three Fiber.',
        href: 'https://github.com/isaacElytraflight/elytraflight-website',
      },
      {
        title: 'Project Two',
        description: 'Placeholder for your next project. Replace this with a real description.',
      },
      {
        title: 'Project Three',
        description: 'Another placeholder — add links, screenshots, or demos here.',
      },
    ],
  },
  {
    id: 'contact',
    title: 'Contact',
    position: [35, 13, 15],
    body: 'Want to collaborate or just say hi? Reach out through any of the links below.',
    links: [
      { label: 'Email', href: 'mailto:hello@elytraflight.com' },
      { label: 'GitHub', href: 'https://github.com/isaacElytraflight' },
      { label: 'LinkedIn', href: 'https://linkedin.com' },
    ],
  },
]
