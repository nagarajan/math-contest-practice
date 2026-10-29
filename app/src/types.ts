export type BankId = 'kangaroo' | 'noetic' | 'moems'

export const BANK_IDS: BankId[] = ['kangaroo', 'noetic', 'moems']

export const BANK_NAMES: Record<BankId, string> = {
  kangaroo: 'Math Kangaroo',
  noetic: 'Noetic',
  moems: 'Math Olympiad (MOEMS)',
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
  points: number | null
  timeMinutes: number | null
  type: 'mc' | 'numeric' | 'text'
  prompt: string
  image: string | null
  choices: Choice[] | null
  answer: string
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
}

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
  practiceBanks: BankId[]
  examQuestionCount: number
}
