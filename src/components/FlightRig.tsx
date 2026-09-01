import { useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { sections, PROXIMITY_RADIUS } from '../data/sections'
import { useFlightStore } from '../store/useFlightStore'
import { PlayerGlider } from './PlayerGlider'

const MOVE_SPEED = 18
const LOOK_SENSITIVITY = 0.002
const MIN_Y = 4
const MAX_Y = 40

const cameraOffset = new THREE.Vector3(0, 2.5, 6)
const tempVec = new THREE.Vector3()
const tempVec2 = new THREE.Vector3()

export function FlightRig() {
  const { camera } = useThree()
  const positionRef = useRef<[number, number, number]>([0, 15, 25])
  const velocityRef = useRef<[number, number, number]>([0, 0, 0])
  const yawRef = useRef(Math.PI)
  const pitchRef = useRef(-0.15)

  const setActiveSection = useFlightStore((s) => s.setActiveSection)

  useFrame((_, delta) => {
    const input = useFlightStore.getState().input
    const dt = Math.min(delta, 0.05)

    yawRef.current -= input.lookX * LOOK_SENSITIVITY
    pitchRef.current = THREE.MathUtils.clamp(
      pitchRef.current - input.lookY * LOOK_SENSITIVITY,
      -0.6,
      0.4,
    )

    useFlightStore.getState().setInput({ lookX: 0, lookY: 0 })

    const forward = new THREE.Vector3(
      Math.sin(yawRef.current),
      0,
      Math.cos(yawRef.current),
    )
    const right = new THREE.Vector3(
      Math.cos(yawRef.current),
      0,
      -Math.sin(yawRef.current),
    )

    const move = tempVec.set(0, 0, 0)
    if (input.forward !== 0) move.addScaledVector(forward, input.forward)
    if (input.right !== 0) move.addScaledVector(right, input.right)
    if (input.up !== 0) move.y += input.up

    if (move.lengthSq() > 0) {
      move.normalize().multiplyScalar(MOVE_SPEED * dt)
    }

    const [px, py, pz] = positionRef.current
    const newX = px + move.x
    const newY = THREE.MathUtils.clamp(py + move.y, MIN_Y, MAX_Y)
    const newZ = pz + move.z

    positionRef.current = [newX, newY, newZ]
    velocityRef.current = [move.x / dt, move.y / dt, move.z / dt]

    const lookTarget = tempVec2.set(newX, newY, newZ)
    const offset = cameraOffset
      .clone()
      .applyAxisAngle(new THREE.Vector3(0, 1, 0), yawRef.current)
    offset.y += pitchRef.current * 3

    const desiredCameraPos = lookTarget.clone().add(offset)
    camera.position.lerp(desiredCameraPos, 1 - Math.pow(0.001, dt))

    const lookAtPoint = lookTarget.clone()
    lookAtPoint.y += 0.5
    camera.lookAt(lookAtPoint)

    let nearest = null
    let nearestDist = Infinity
    for (const section of sections) {
      const [sx, sy, sz] = section.position
      const dist = Math.hypot(newX - sx, newY - sy, newZ - sz)
      if (dist < nearestDist) {
        nearestDist = dist
        nearest = section
      }
    }

    if (nearest && nearestDist <= PROXIMITY_RADIUS) {
      setActiveSection(nearest)
    } else {
      setActiveSection(null)
    }
  })

  return (
    <PlayerGlider positionRef={positionRef} velocityRef={velocityRef} />
  )
}
