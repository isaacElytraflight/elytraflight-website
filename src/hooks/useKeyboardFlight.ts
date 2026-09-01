import { useEffect } from 'react'
import { useFlightStore } from '../store/useFlightStore'

const KEY_MAP: Record<string, keyof ReturnType<typeof useFlightStore.getState>['input']> = {
  KeyW: 'forward',
  KeyS: 'forward',
  KeyA: 'right',
  KeyD: 'right',
  Space: 'up',
  ShiftLeft: 'up',
  ShiftRight: 'up',
}

export function useKeyboardFlight() {
  const setInput = useFlightStore((s) => s.setInput)
  const isFlying = useFlightStore((s) => s.isFlying)
  const isMobile = useFlightStore((s) => s.isMobile)

  useEffect(() => {
    if (isMobile) return

    const pressed = new Set<string>()

    const updateInput = () => {
      setInput({
        forward: (pressed.has('KeyW') ? -1 : 0) + (pressed.has('KeyS') ? 1 : 0),
        right: (pressed.has('KeyD') ? 1 : 0) + (pressed.has('KeyA') ? -1 : 0),
        up:
          (pressed.has('Space') ? 1 : 0) +
          (pressed.has('ShiftLeft') || pressed.has('ShiftRight') ? -1 : 0),
      })
    }

    const onKeyDown = (e: KeyboardEvent) => {
      if (!KEY_MAP[e.code]) return
      e.preventDefault()
      pressed.add(e.code)
      updateInput()
    }

    const onKeyUp = (e: KeyboardEvent) => {
      if (!KEY_MAP[e.code]) return
      e.preventDefault()
      pressed.delete(e.code)
      updateInput()
    }

    const onBlur = () => {
      pressed.clear()
      updateInput()
    }

    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    window.addEventListener('blur', onBlur)

    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
      window.removeEventListener('blur', onBlur)
    }
  }, [isMobile, setInput])

  useEffect(() => {
    if (isMobile || !isFlying) return

    const onMouseMove = (e: MouseEvent) => {
      if (document.pointerLockElement) {
        useFlightStore.getState().setInput({
          lookX: e.movementX,
          lookY: e.movementY,
        })
      }
    }

    const onPointerLockChange = () => {
      if (!document.pointerLockElement) {
        useFlightStore.getState().setIsFlying(false)
        useFlightStore.getState().resetInput()
      }
    }

    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('pointerlockchange', onPointerLockChange)

    return () => {
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('pointerlockchange', onPointerLockChange)
    }
  }, [isFlying, isMobile])
}

export function requestFlightLock() {
  const canvas = document.querySelector('canvas')
  if (canvas?.requestPointerLock) {
    canvas.requestPointerLock()
    useFlightStore.getState().setIsFlying(true)
  }
}
