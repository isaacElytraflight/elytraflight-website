import { Sky } from '@react-three/drei'
import { sections } from '../data/sections'
import { CloudField } from './CloudField'
import { FlightRig } from './FlightRig'
import { Island } from './Island'

export function World() {
  return (
    <>
      <color attach="background" args={['#6eb5ff']} />
      <fog attach="fog" args={['#ffe8d0', 30, 120]} />

      <Sky
        distance={450000}
        sunPosition={[100, 20, 100]}
        inclination={0.52}
        azimuth={0.25}
        mieCoefficient={0.005}
        mieDirectionalG={0.8}
        rayleigh={0.5}
        turbidity={8}
      />

      <ambientLight intensity={0.5} color="#8eb9ff" />
      <directionalLight
        position={[100, 40, 80]}
        intensity={1.4}
        color="#ffd699"
        castShadow
        shadow-mapSize={[1024, 1024]}
      />

      <CloudField />

      {sections.map((section) => (
        <Island key={section.id} section={section} />
      ))}

      <FlightRig />
    </>
  )
}
