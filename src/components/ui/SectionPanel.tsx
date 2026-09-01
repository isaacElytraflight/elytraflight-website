import { useFlightStore } from '../../store/useFlightStore'

export function SectionPanel() {
  const activeSection = useFlightStore((s) => s.activeSection)

  if (!activeSection) return null

  return (
    <div className="section-panel">
      <div className="section-card">
        {activeSection.id === 'about' && (
          <img
            src="/profile.png"
            alt="Profile"
            className="section-profile"
          />
        )}
        <h2>{activeSection.title}</h2>
        <p>{activeSection.body}</p>

        {activeSection.projects && (
          <ul className="project-list">
            {activeSection.projects.map((project) => (
              <li key={project.title} className="project-item">
                <h3>{project.title}</h3>
                <p>{project.description}</p>
                {project.href && (
                  <a href={project.href} target="_blank" rel="noopener noreferrer">
                    View project
                  </a>
                )}
              </li>
            ))}
          </ul>
        )}

        {activeSection.links && (
          <div className="section-links">
            {activeSection.links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
              >
                {link.label}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
