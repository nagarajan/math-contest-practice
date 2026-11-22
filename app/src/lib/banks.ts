import type { BankId, BankMeta, ExamKind, Grade, Question, Solution } from '../types'

export interface BankIndex {
  banks: BankMeta[]
  /** Questions available per grade (all banks). */
  gradeCounts: Record<string, number>
}

export interface LoadedBanks {
  grade: Grade
  all: Question[]
  byId: Map<string, Question>
  /** Banks that have questions for this grade, in display order. */
  banks: BankMeta[]
}

export const assetUrl = (p: string) => `${import.meta.env.BASE_URL}${p.replace(/^\//, '')}`

export async function loadIndex(): Promise<BankIndex> {
  const r = await fetch(assetUrl('banks/index.json'))
  if (!r.ok) throw new Error(`index.json: HTTP ${r.status}`)
  return r.json()
}

const gradeCache = new Map<Grade, Promise<Question[]>>()

export function loadGradeQuestions(g: Grade): Promise<Question[]> {
  let p = gradeCache.get(g)
  if (!p) {
    p = fetch(assetUrl(`banks/grade-${g}.json`)).then((r) => (r.ok ? r.json() : []))
    p.catch(() => gradeCache.delete(g))
    gradeCache.set(g, p)
  }
  return p
}

export async function loadGrade(index: BankIndex, g: Grade): Promise<LoadedBanks> {
  const all = await loadGradeQuestions(g)
  return {
    grade: g,
    all,
    byId: new Map(all.map((q) => [q.id, q])),
    banks: index.banks.filter((b) => (b.countsByGrade[String(g)] ?? 0) > 0),
  }
}

/** Look up questions from several grades (history can span grade changes). */
export async function loadLookup(grades: Grade[]): Promise<Map<string, Question>> {
  const lists = await Promise.all([...new Set(grades)].map(loadGradeQuestions))
  const m = new Map<string, Question>()
  for (const l of lists) for (const q of l) m.set(q.id, q)
  return m
}

export function bankMeta(index: BankIndex, id: BankId | null | undefined): BankMeta | undefined {
  return index.banks.find((b) => b.id === id)
}

export const bankName = (index: BankIndex, id: BankId | null | undefined) => bankMeta(index, id)?.name ?? String(id ?? '')

export const isAutoGraded = (q: Question) => q.type !== 'self'

export function examTitle(index: BankIndex, e: { kind: ExamKind; bank: BankId | null }) {
  return e.kind === 'mixed' ? 'Mixed exam' : `Focused exam · ${bankName(index, e.bank)}`
}

const solCache = new Map<string, Promise<Record<string, Solution[]>>>()

export function loadSolutions(q: Question): Promise<Solution[]> {
  if (q.solutions) return Promise.resolve(q.solutions)
  if (!q.sol) return Promise.resolve([])
  let p = solCache.get(q.sol)
  if (!p) {
    p = fetch(assetUrl(`banks/sol/${q.sol}.json`)).then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      return r.json()
    })
    p.catch(() => solCache.delete(q.sol!))
    solCache.set(q.sol, p)
  }
  return p.then((m) => m[q.id] ?? [])
}
