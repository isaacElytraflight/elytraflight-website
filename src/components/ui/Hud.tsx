import { useFlightStore } from '../../store/useFlightStore'

export function Hud() {
  const activeSection = useFlightStore((s) => s.activeSection)
  const isFlying = useFlightStore((s) => s.isFlying)
  const isMobile = useFlightStore((s) => s.isMobile)

  return (
    <div className="hud">
      <header className="hud-header">
        <div className="hud-brand">
          <img src="/profile.png" alt="" className="hud-profile" />
          <h1 className="hud-title">Elytraflight</h1>
        </div>
        {activeSection && (
          <span className="hud-island">Near: {activeSection.title}</span>
        )}
      </header>

      {!isFlying && (
        <div className="fly-prompt">
          {isMobile ? (
            <p>Tap and drag to fly. Left side moves, right side looks.</p>
          ) : (
            <p>Click anywhere to start flying</p>
          )}
          {!isMobile && (
            <p className="fly-hint">WASD to move · Space/Shift for altitude · Mouse to look</p>
          )}
        </div>
      )}

      {isMobile && isFlying && (
        <div className="mobile-zones">
          <div className="zone zone-move">Move</div>
          <div className="zone zone-look">Look</div>
        </div>
      )}
    </div>
  )
}
