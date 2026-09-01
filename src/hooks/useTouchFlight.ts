import { useCallback, useRef } from 'react'
import { useFlightStore } from '../store/useFlightStore'

type TouchId = number

type ActiveTouch = {
  id: TouchId
  startX: number
  startY: number
  lastX: number
  lastY: number
  side: 'move' | 'look'
}

export function useTouchFlight() {
  const touchesRef = useRef<Map<TouchId, ActiveTouch>>(new Map())

  const onTouchStart = useCallback((e: React.TouchEvent) => {
    const width = window.innerWidth
    for (const touch of Array.from(e.changedTouches)) {
      const side: 'move' | 'look' = touch.clientX < width / 2 ? 'move' : 'look'
      touchesRef.current.set(touch.identifier, {
        id: touch.identifier,
        startX: touch.clientX,
        startY: touch.clientY,
        lastX: touch.clientX,
        lastY: touch.clientY,
        side,
      })
    }
    useFlightStore.getState().setIsFlying(true)
  }, [])

  const onTouchMove = useCallback((e: React.TouchEvent) => {
    e.preventDefault()
    let forward = 0
    let right = 0
    let up = 0
    let lookX = 0
    let lookY = 0

    for (const touch of Array.from(e.changedTouches)) {
      const active = touchesRef.current.get(touch.identifier)
      if (!active) continue

      const dx = touch.clientX - active.lastX
      const dy = touch.clientY - active.lastY
      active.lastX = touch.clientX
      active.lastY = touch.clientY

      if (active.side === 'look') {
        lookX += dx
        lookY += dy
      } else {
        const offsetX = touch.clientX - active.startX
        const offsetY = touch.clientY - active.startY
        const maxDist = 60
        right = Math.max(-1, Math.min(1, offsetX / maxDist))
        forward = Math.max(-1, Math.min(1, -offsetY / maxDist))
        up = Math.max(-1, Math.min(1, -offsetY / maxDist * 0.3))
      }
    }

    useFlightStore.getState().setInput({ forward, right, up, lookX, lookY })
  }, [])

  const onTouchEnd = useCallback((e: React.TouchEvent) => {
    for (const touch of Array.from(e.changedTouches)) {
      touchesRef.current.delete(touch.identifier)
    }
    if (touchesRef.current.size === 0) {
      useFlightStore.getState().resetInput()
    }
  }, [])

  return { onTouchStart, onTouchMove, onTouchEnd }
}
