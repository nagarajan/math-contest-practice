import type { Attempt, ExamRecord, Profile, ProfileData, Settings } from '../types'

const PREFIX = 'mcp:v1:'
const KEY_PROFILES = PREFIX + 'profiles'
const KEY_SETTINGS = PREFIX + 'settings'
const KEY_ACTIVE = PREFIX + 'activeProfile'
const dataKey = (pid: string) => `${PREFIX}data:${pid}`

export const DEFAULT_SETTINGS: Settings = {
  theme: 'system',
  examTimeLimitMin: null,
  practiceBanks: ['kangaroo', 'noetic', 'moems'],
  examQuestionCount: 30,
}

export function emptyData(): ProfileData {
  return { attempts: [], exams: [], stats: {}, seq: 0, examInProgress: null }
}

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

function write(key: string, value: unknown) {
  localStorage.setItem(key, JSON.stringify(value))
}

export function loadProfiles(): Profile[] {
  return read<Profile[]>(KEY_PROFILES, [])
}

export function saveProfiles(p: Profile[]) {
  write(KEY_PROFILES, p)
}

export function loadSettings(): Settings {
  return { ...DEFAULT_SETTINGS, ...read<Partial<Settings>>(KEY_SETTINGS, {}) }
}

export function saveSettings(s: Settings) {
  write(KEY_SETTINGS, s)
}

export function loadActiveProfileId(): string | null {
  return read<string | null>(KEY_ACTIVE, null)
}

export function saveActiveProfileId(id: string | null) {
  write(KEY_ACTIVE, id)
}

export function loadData(pid: string): ProfileData {
  return { ...emptyData(), ...read<Partial<ProfileData>>(dataKey(pid), {}) }
}

export function saveData(pid: string, d: ProfileData) {
  write(dataKey(pid), d)
}

export function deleteData(pid: string) {
  localStorage.removeItem(dataKey(pid))
}

export function eraseEverything() {
  Object.keys(localStorage)
    .filter((k) => k.startsWith(PREFIX))
    .forEach((k) => localStorage.removeItem(k))
}

/** Record an answered question and update the scheduler state. Returns new data (immutable). */
export function recordAttempt(d: ProfileData, a: Attempt): ProfileData {
  const prev = d.stats[a.qid]
  const seq = d.seq + 1
  return {
    ...d,
    seq,
    attempts: [...d.attempts, a],
    stats: {
      ...d.stats,
      [a.qid]: {
        seen: (prev?.seen ?? 0) + 1,
        correct: (prev?.correct ?? 0) + (a.correct ? 1 : 0),
        lastCorrect: a.correct,
        streak: a.correct ? (prev?.streak ?? 0) + 1 : 0,
        lastAt: a.at,
        lastSeq: seq,
      },
    },
  }
}

export function recordExam(d: ProfileData, exam: ExamRecord, attempts: Attempt[]): ProfileData {
  let out: ProfileData = { ...d, exams: [...d.exams, exam], examInProgress: null }
  for (const a of attempts) out = recordAttempt(out, a)
  return out
}

export function newId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}
