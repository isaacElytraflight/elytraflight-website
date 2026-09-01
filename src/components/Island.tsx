import { Html } from '@react-three/drei'
import type { Section } from '../data/sections'

type IslandProps = {
  section: Section
}

export function Island({ section }: IslandProps) {
  const [x, y, z] = section.position

  return (
    <group position={[x, y, z]}>
      <mesh position={[0, -2, 0]} castShadow receiveShadow>
        <boxGeometry args={[4, 8, 4]} />
        <meshStandardMaterial color="#6b6b6b" roughness={0.9} />
      </mesh>
      <mesh position={[0, 2.25, 0]} castShadow receiveShadow>
        <boxGeometry args={[5, 0.5, 5]} />
        <meshStandardMaterial color="#4a9e3f" roughness={0.85} />
      </mesh>
      <mesh position={[0, 2.6, 0]} castShadow>
        <boxGeometry args={[4.5, 0.2, 4.5]} />
        <meshStandardMaterial color="#5cb849" roughness={0.8} />
      </mesh>
      <Html
        position={[0, 5, 0]}
        center
        distanceFactor={12}
        style={{ pointerEvents: 'none' }}
      >
        <div className="island-label">{section.title}</div>
      </Html>
    </group>
  )
}
