import { create } from 'zustand'
import type { Section } from '../data/sections'

type FlightInput = {
  forward: number
  right: number
  up: number
  lookX: number
  lookY: number
}

type FlightStore = {
  activeSection: Section | null
  setActiveSection: (section: Section | null) => void
  isFlying: boolean
  setIsFlying: (flying: boolean) => void
  isMobile: boolean
  setIsMobile: (mobile: boolean) => void
  input: FlightInput
  setInput: (partial: Partial<FlightInput>) => void
  resetInput: () => void
}

const defaultInput: FlightInput = {
  forward: 0,
  right: 0,
  up: 0,
  lookX: 0,
  lookY: 0,
}

export const useFlightStore = create<FlightStore>((set) => ({
  activeSection: null,
  setActiveSection: (section) => set({ activeSection: section }),
  isFlying: false,
  setIsFlying: (flying) => set({ isFlying: flying }),
  isMobile: false,
  setIsMobile: (mobile) => set({ isMobile: mobile }),
  input: { ...defaultInput },
  setInput: (partial) =>
    set((state) => ({ input: { ...state.input, ...partial } })),
  resetInput: () => set({ input: { ...defaultInput } }),
}))
