import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { profileGrade, type Grade, type Profile, type ProfileData, type Settings } from './types'
import { loadGrade, type BankIndex, type LoadedBanks } from './lib/banks'
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
  index: BankIndex
  /** Questions for the active profile's grade. */
  banks: LoadedBanks
  profiles: Profile[]
  profile: Profile | null
  grade: Grade
  data: ProfileData
  settings: Settings
  setSettings: (s: Settings) => void
  updateData: (fn: (d: ProfileData) => ProfileData) => void
  selectProfile: (id: string | null) => void
  addProfile: (name: string, avatar: string, grade: Grade) => Profile
  updateProfile: (id: string, patch: Partial<Omit<Profile, 'id'>>) => void
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

export function AppProvider({ index, children }: { index: BankIndex; children: ReactNode }) {
  const [profiles, setProfiles] = useState<Profile[]>(loadProfiles)
  const [activeId, setActiveId] = useState<string | null>(() => {
    const id = loadActiveProfileId()
    return id && loadProfiles().some((p) => p.id === id) ? id : null
  })
  const [data, setData] = useState<ProfileData>(() => (activeId ? loadData(activeId) : emptyData()))
  const [settings, setSettingsState] = useState<Settings>(loadSettings)
  const [banks, setBanks] = useState<LoadedBanks | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  const profile = profiles.find((p) => p.id === activeId) ?? null
  const grade = profileGrade(profile)

  useEffect(() => {
    saveActiveProfileId(activeId)
    setData(activeId ? loadData(activeId) : emptyData())
  }, [activeId])

  useEffect(() => {
    let live = true
    setLoadError(null)
    loadGrade(index, grade)
      .then((b) => live && setBanks(b))
      .catch((e) => live && setLoadError(String(e)))
    return () => {
      live = false
    }
  }, [index, grade])

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

  const value = useMemo<AppState | null>(
    () =>
      banks && banks.grade === grade
        ? {
            index,
            banks,
            profiles,
            profile,
            grade,
            data,
            settings,
            setSettings,
            updateData,
            selectProfile: setActiveId,
            addProfile: (name, avatar, g) => {
              const p: Profile = { id: newId(), name: name.trim(), avatar, grade: g, createdAt: Date.now() }
              const next = [...profiles, p]
              setProfiles(next)
              saveProfiles(next)
              return p
            },
            updateProfile: (id, patch) => {
              const next = profiles.map((p) => (p.id === id ? { ...p, ...patch, name: (patch.name ?? p.name).trim() } : p))
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
          }
        : null,
    [index, banks, grade, profiles, profile, data, settings, setSettings, updateData, activeId],
  )

  if (loadError) return <div className="loading">Could not load the questions: {loadError}</div>
  if (!value) return <div className="loading">Loading questions…</div>
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}
