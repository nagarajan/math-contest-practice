import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { Profile, ProfileData, Settings } from './types'
import type { LoadedBanks } from './lib/banks'
import {
  deleteData,
  eraseEverything,
  loadActiveProfileId,
  loadData,
  loadProfiles,
  loadSettings,
  newId,
  saveActiveProfileId,
  saveData,
  saveProfiles,
  saveSettings,
  emptyData,
  DEFAULT_SETTINGS,
} from './lib/storage'

interface AppState {
  banks: LoadedBanks
  profiles: Profile[]
  profile: Profile | null
  data: ProfileData
  settings: Settings
  setSettings: (s: Settings) => void
  updateData: (fn: (d: ProfileData) => ProfileData) => void
  selectProfile: (id: string | null) => void
  addProfile: (name: string, avatar: string) => Profile
  renameProfile: (id: string, name: string, avatar: string) => void
  removeProfile: (id: string) => void
  clearHistory: () => void
  resetApp: () => void
}

const Ctx = createContext<AppState | null>(null)

export function useApp(): AppState {
  const v = useContext(Ctx)
  if (!v) throw new Error('useApp outside provider')
  return v
}

export function AppProvider({ banks, children }: { banks: LoadedBanks; children: ReactNode }) {
  const [profiles, setProfiles] = useState<Profile[]>(loadProfiles)
  const [activeId, setActiveId] = useState<string | null>(() => {
    const id = loadActiveProfileId()
    return id && loadProfiles().some((p) => p.id === id) ? id : null
  })
  const [data, setData] = useState<ProfileData>(() => (activeId ? loadData(activeId) : emptyData()))
  const [settings, setSettingsState] = useState<Settings>(loadSettings)

  const profile = profiles.find((p) => p.id === activeId) ?? null

  useEffect(() => {
    saveActiveProfileId(activeId)
    setData(activeId ? loadData(activeId) : emptyData())
  }, [activeId])

  const updateData = useCallback(
    (fn: (d: ProfileData) => ProfileData) => {
      setData((d) => {
        const next = fn(d)
        if (activeId) saveData(activeId, next)
        return next
      })
    },
    [activeId],
  )

  const setSettings = useCallback((s: Settings) => {
    setSettingsState(s)
    saveSettings(s)
  }, [])

  const value = useMemo<AppState>(
    () => ({
      banks,
      profiles,
      profile,
      data,
      settings,
      setSettings,
      updateData,
      selectProfile: setActiveId,
      addProfile: (name, avatar) => {
        const p: Profile = { id: newId(), name: name.trim(), avatar, createdAt: Date.now() }
        const next = [...profiles, p]
        setProfiles(next)
        saveProfiles(next)
        return p
      },
      renameProfile: (id, name, avatar) => {
        const next = profiles.map((p) => (p.id === id ? { ...p, name: name.trim(), avatar } : p))
        setProfiles(next)
        saveProfiles(next)
      },
      removeProfile: (id) => {
        const next = profiles.filter((p) => p.id !== id)
        setProfiles(next)
        saveProfiles(next)
        deleteData(id)
        if (activeId === id) setActiveId(null)
      },
      clearHistory: () => {
        if (!activeId) return
        const fresh = emptyData()
        saveData(activeId, fresh)
        setData(fresh)
      },
      resetApp: () => {
        eraseEverything()
        setProfiles([])
        setActiveId(null)
        setData(emptyData())
        setSettingsState(DEFAULT_SETTINGS)
      },
    }),
    [banks, profiles, profile, data, settings, setSettings, updateData, activeId],
  )

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}
