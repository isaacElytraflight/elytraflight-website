import { useEffect, useState } from 'react'
import { Experience } from './components/Experience'
import { Hud } from './components/ui/Hud'
import { SectionPanel } from './components/ui/SectionPanel'
import { useKeyboardFlight, requestFlightLock } from './hooks/useKeyboardFlight'
import { useTouchFlight } from './hooks/useTouchFlight'
import { useFlightStore } from './store/useFlightStore'
import './styles/global.css'

function App() {
  const [loaded, setLoaded] = useState(false)
  const isMobile = useFlightStore((s) => s.isMobile)
  const setIsMobile = useFlightStore((s) => s.setIsMobile)
  const { onTouchStart, onTouchMove, onTouchEnd } = useTouchFlight()

  useKeyboardFlight()

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.matchMedia('(pointer: coarse)').matches || window.innerWidth < 768)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [setIsMobile])

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 800)
    return () => clearTimeout(timer)
  }, [])

  const handleStartFlight = () => {
    if (!isMobile) {
      requestFlightLock()
    } else {
      useFlightStore.getState().setIsFlying(true)
    }
  }

  if (!loaded) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <h1>Elytraflight</h1>
          <p>Preparing for takeoff...</p>
          <div className="loading-spinner" />
        </div>
      </div>
    )
  }

  return (
    <div
      className="app"
      onTouchStart={isMobile ? onTouchStart : undefined}
      onTouchMove={isMobile ? onTouchMove : undefined}
      onTouchEnd={isMobile ? onTouchEnd : undefined}
    >
      <div className="canvas-container" onClick={!isMobile ? handleStartFlight : undefined}>
        <Experience />
      </div>
      {isMobile && (
        <button className="fly-button" onClick={handleStartFlight} type="button">
          Fly
        </button>
      )}
      <Hud />
      <SectionPanel />
    </div>
  )
}

export default App
