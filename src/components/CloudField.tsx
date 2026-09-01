import { Cloud } from '@react-three/drei'
import { useMemo } from 'react'

const CLOUD_POSITIONS: [number, number, number][] = [
  [-20, 5, -15],
  [15, 3, -25],
  [-10, 7, 20],
  [30, 4, 5],
  [-35, 6, -5],
  [5, 2, 35],
  [-25, 8, 25],
  [40, 5, -10],
  [0, 3, 0],
  [-15, 4, -35],
  [25, 6, 30],
  [-40, 5, 15],
]

export function CloudField() {
  const clouds = useMemo(
    () =>
      CLOUD_POSITIONS.map((position, i) => ({
        position,
        scale: 0.8 + (i % 3) * 0.4,
        seed: i + 1,
      })),
    [],
  )

  return (
    <group>
      {clouds.map((cloud) => (
        <Cloud
          key={cloud.seed}
          position={cloud.position}
          scale={cloud.scale}
          opacity={0.55}
          speed={0.15}
          segments={16}
          bounds={[8, 2, 8]}
          color="#fff8f0"
        />
      ))}
    </group>
  )
}
