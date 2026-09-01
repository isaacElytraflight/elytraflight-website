import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import { World } from './World'

export function Experience() {
  const dpr = Math.min(window.devicePixelRatio, 1.5)

  return (
    <Canvas
      shadows
      dpr={dpr}
      camera={{ fov: 60, near: 0.1, far: 500, position: [0, 15, 35] }}
      gl={{ antialias: true, alpha: false }}
    >
      <Suspense fallback={null}>
        <World />
      </Suspense>
    </Canvas>
  )
}
