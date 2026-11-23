import type { BankId, BankMeta, ExamKind, Grade, Question, Solution } from '../types'

export interface ChunkMeta {
  file: string
  bank: BankId
  grades: Grade[]
  count: number
}

export interface BankIndex {
  banks: BankMeta[]
  /** Questions available per grade (all banks). */
  gradeCounts: Record<string, number>
  /** Question files, one per bank and set of grades. */
  chunks: ChunkMeta[]
}

type PaperRef = [string | null, Omit<Question['source'], 'number'>]
type StoredQuestion = Partial<Question> & { id: string; p: number; n?: number | string }
interface StoredChunk {
  bank: BankId
  grades: Grade[]
  papers: PaperRef[]
  questions: StoredQuestion[]
}

export function expandChunk(c: StoredChunk): Question[] {
  return c.questions.map(({ p, n, ...q }) => {
    const [sol, source] = c.papers[p]
    return {
      points: null,
      timeMinutes: null,
      image: null,
      choices: null,
      answer: '',
      acceptedAnswers: null,
      answerUnit: null,
      topics: [],
      difficulty: 1,
      type: 'numeric',
      prompt: '',
      grade: '',
      ...q,
      bank: c.bank,
      grades: c.grades,
      source: { ...source, number: n ?? null },
      sol,
    } as Question
  })
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
  const r = await fetch(assetUrl('banks/index.json'), { cache: 'no-cache' })
  if (!r.ok) throw new Error(`index.json: HTTP ${r.status}`)
  return r.json()
}

const chunkCache = new Map<string, Promise<Question[]>>()

function loadChunk(file: string): Promise<Question[]> {
  let p = chunkCache.get(file)
  if (!p) {
    p = fetch(assetUrl(`banks/${file}`)).then((r) => {
      if (!r.ok) throw new Error(`${file}: HTTP ${r.status}`)
      return r.json().then(expandChunk)
    })
    p.catch(() => chunkCache.delete(file))
    chunkCache.set(file, p)
  }
  return p
}

export async function loadGradeQuestions(index: BankIndex, g: Grade): Promise<Question[]> {
  const lists = await Promise.all(index.chunks.filter((c) => c.grades.includes(g)).map((c) => loadChunk(c.file)))
  return lists.flat()
}

export async function loadGrade(index: BankIndex, g: Grade): Promise<LoadedBanks> {
  const all = await loadGradeQuestions(index, g)
  return {
    grade: g,
    all,
    byId: new Map(all.map((q) => [q.id, q])),
    banks: index.banks.filter((b) => (b.countsByGrade[String(g)] ?? 0) > 0),
  }
}

/** Look up questions from several grades (history can span grade changes). */
export async function loadLookup(index: BankIndex, grades: Grade[]): Promise<Map<string, Question>> {
  const lists = await Promise.all([...new Set(grades)].map((g) => loadGradeQuestions(index, g)))
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
