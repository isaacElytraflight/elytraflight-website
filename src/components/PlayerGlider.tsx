import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import type { Group } from 'three'
import { useFlightStore } from '../store/useFlightStore'

type PlayerGliderProps = {
  positionRef: React.MutableRefObject<[number, number, number]>
  velocityRef: React.MutableRefObject<[number, number, number]>
}

export function PlayerGlider({ positionRef, velocityRef }: PlayerGliderProps) {
  const groupRef = useRef<Group>(null)
  const isFlying = useFlightStore((s) => s.isFlying)

  useFrame((_, delta) => {
    if (!groupRef.current) return
    const [x, y, z] = positionRef.current
    groupRef.current.position.set(x, y, z)

    const [vx, , vz] = velocityRef.current
    const targetPitch = -vz * 0.08
    const targetRoll = -vx * 0.12

    groupRef.current.rotation.x += (targetPitch - groupRef.current.rotation.x) * 8 * delta
    groupRef.current.rotation.z += (targetRoll - groupRef.current.rotation.z) * 8 * delta

    const bob = isFlying ? Math.sin(Date.now() * 0.003) * 0.05 : 0
    groupRef.current.position.y = y + bob
  })

  return (
    <group ref={groupRef}>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[0.4, 0.6, 0.3]} />
        <meshStandardMaterial color="#e8e0d4" />
      </mesh>
      <mesh position={[-1.2, 0.1, 0]} rotation={[0, 0, 0.3]}>
        <boxGeometry args={[1.8, 0.05, 0.8]} />
        <meshStandardMaterial color="#f5f5f5" emissive="#ffffff" emissiveIntensity={0.1} />
      </mesh>
      <mesh position={[1.2, 0.1, 0]} rotation={[0, 0, -0.3]}>
        <boxGeometry args={[1.8, 0.05, 0.8]} />
        <meshStandardMaterial color="#f5f5f5" emissive="#ffffff" emissiveIntensity={0.1} />
      </mesh>
    </group>
  )
}
