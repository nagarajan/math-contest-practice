/** Bank ids come from data/banks.json (e.g. "kangaroo", "amc8", "putnam"). */
export type BankId = string

/** US school grade 1-12; 13 = undergraduate, 14 = graduate. */
export type Grade = number

export const GRADES: Grade[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

export function gradeName(g: Grade, short = false): string {
  if (g === 13) return short ? 'Undergrad' : 'Undergraduate'
  if (g === 14) return 'Graduate'
  const suffix = g === 1 ? 'st' : g === 2 ? 'nd' : g === 3 ? 'rd' : 'th'
  return short ? `Grade ${g}` : `${g}${suffix} grade`
}

export interface BankMeta {
  id: BankId
  name: string
  description: string
  /** Pill colour in the UI. */
  color: string
  /** Points for a blank answer in an exam (AMC: 1.5). Default 0. */
  blankPoints?: number
  /** Points for a wrong answer in an exam (negative = penalty). Default 0. */
  wrongPoints?: number
  /** Questions in a real paper, used as the default length of a focused exam. */
  examLength?: number
  /** Official time for one paper, shown as a hint. */
  examMinutes?: number
  scoringNote: string
  count: number
  countsByGrade: Record<string, number>
  /** Auto-gradable questions (usable in exams) per grade. */
  examCountsByGrade: Record<string, number>
  sources: { contest: string; paper: string; year: number | null; count: number; url: string; grades: Grade[] }[]
}

export interface Choice {
  key: string
  text: string
  image?: string | null
}

export interface Solution {
  title: string
  body: string
}

/**
 * mc / numeric / text are checked automatically. "self" questions (proofs and answers that
 * cannot be typed reliably) are self-graded after reading the solution, and are practice-only.
 */
export type QuestionType = 'mc' | 'numeric' | 'text' | 'self'

export interface Question {
  id: string
  bank: BankId
  source: {
    contest: string
    paper: string
    year: number | null
    number: number | string | null
    url: string
  }
  grade: string
  grades: Grade[]
  points: number | null
  timeMinutes: number | null
  type: QuestionType
  prompt: string
  image: string | null
  choices: Choice[] | null
  /** For "numeric", a number or plain expression (e.g. "3*sqrt(2)/4"); for "self", Markdown. */
  answer: string
  /** Optional Markdown/KaTeX rendering of the answer for display (e.g. "$\\frac{3\\sqrt2}{4}$"). */
  answerDisplay?: string | null
  acceptedAnswers: string[] | null
  answerUnit: string | null
  solutions: Solution[]
  topics: string[]
  difficulty: 1 | 2 | 3
  reviewNote?: string | null
}

export interface Profile {
  id: string
  name: string
  avatar: string
  createdAt: number
  grade?: Grade
}

export const DEFAULT_GRADE: Grade = 5

export const profileGrade = (p: Profile | null | undefined): Grade => p?.grade ?? DEFAULT_GRADE

/** One answered question, from practice or an exam. */
export interface Attempt {
  qid: string
  bank: BankId
  answer: string
  correct: boolean
  at: number
  ms: number
  mode: 'practice' | 'exam'
  examId?: string
  /** Grade the profile was practising at (to find the question again). Missing = 5. */
  grade?: Grade
  /** True when the student marked a self-graded question themselves. */
  selfGraded?: boolean
}

export interface ExamQuestionResult {
  qid: string
  answer: string
  correct: boolean
  points: number
  maxPoints: number
}

export type ExamKind = 'mixed' | 'focused'

export interface ExamRecord {
  id: string
  kind: ExamKind
  bank: BankId | null
  grade?: Grade
  startedAt: number
  finishedAt: number
  elapsedMs: number
  timeLimitMin: number | null
  timedOut: boolean
  results: ExamQuestionResult[]
  score: number
  maxScore: number
  correctCount: number
}

export interface ExamInProgress {
  id: string
  kind: ExamKind
  bank: BankId | null
  grade?: Grade
  qids: string[]
  answers: Record<string, string>
  flagged: string[]
  current: number
  startedAt: number
  /** Accumulated time from earlier sessions (exam survives a page reload). */
  elapsedBeforeMs: number
  resumedAt: number
  timeLimitMin: number | null
}

/** Per-question learning state used by the practice scheduler. */
export interface QuestionStat {
  seen: number
  correct: number
  lastCorrect: boolean
  /** Consecutive correct answers in a row (reset on a wrong answer). */
  streak: number
  lastAt: number
  /** Value of the profile's practice counter when this question was last answered. */
  lastSeq: number
}

export interface ProfileData {
  attempts: Attempt[]
  exams: ExamRecord[]
  stats: Record<string, QuestionStat>
  /** Number of questions answered so far (practice + exam); used for "at least 10 questions" spacing. */
  seq: number
  examInProgress: ExamInProgress | null
}

export type ThemePref = 'light' | 'dark' | 'system'

export interface Settings {
  theme: ThemePref
  examTimeLimitMin: number | null
  /** Banks left out of general practice (new banks are included automatically). */
  practiceExcluded: BankId[]
  examQuestionCount: number
  /** Include self-graded (proof / free-form) problems in general practice. */
  practiceSelfGraded: boolean
}
