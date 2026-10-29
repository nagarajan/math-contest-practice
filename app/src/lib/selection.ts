import type { BankId, ProfileData, Question, QuestionStat } from '../types'

/** A wrong question may come back only after this many other questions... */
export const RETRY_AFTER_QUESTIONS = 10
/** ...or after this much time, whichever comes first. */
export const RETRY_AFTER_MS = 60 * 60 * 1000

/**
 * Relative selection weights. Wrong > unseen > correct, as required:
 * questions answered wrong come back more often than new ones, and questions answered
 * right come back less often than both (and less with every further correct answer).
 */
export const WEIGHT_WRONG = 3
export const WEIGHT_UNSEEN = 1
export const WEIGHT_CORRECT = 0.2

export function questionWeight(stat: QuestionStat | undefined, seq: number, now: number): number {
  if (!stat || stat.seen === 0) return WEIGHT_UNSEEN
  const spacedOut = seq - stat.lastSeq >= RETRY_AFTER_QUESTIONS || now - stat.lastAt >= RETRY_AFTER_MS
  if (!spacedOut) return 0
  if (!stat.lastCorrect) return WEIGHT_WRONG
  return WEIGHT_CORRECT / Math.max(1, stat.streak)
}

function weightedPick<T>(items: T[], weights: number[], rand: () => number): number {
  const total = weights.reduce((a, b) => a + b, 0)
  if (total <= 0) return -1
  let r = rand() * total
  for (let i = 0; i < items.length; i++) {
    r -= weights[i]
    if (r < 0) return i
  }
  return items.length - 1
}

export function pickPracticeQuestion(
  questions: Question[],
  data: ProfileData,
  banks: BankId[],
  excludeId: string | null,
  now = Date.now(),
  rand: () => number = Math.random,
): Question | null {
  const pool = questions.filter((q) => banks.includes(q.bank) && q.id !== excludeId)
  if (!pool.length) return null
  const weights = pool.map((q) => questionWeight(data.stats[q.id], data.seq, now))
  let idx = weightedPick(pool, weights, rand)
  if (idx < 0) {
    // Every question is cooling down (tiny bank or very fast session): fall back to the
    // one seen longest ago so practice never gets stuck.
    idx = pool.reduce(
      (best, q, i) => ((data.stats[q.id]?.lastSeq ?? -1) < (data.stats[pool[best].id]?.lastSeq ?? -1) ? i : best),
      0,
    )
  }
  return pool[idx]
}

/**
 * Build an exam: questions never used in an earlier exam are preferred, then the set is
 * ordered easy -> hard like a real contest. A focused Kangaroo exam keeps the official
 * 3/4/5-point structure (one third of each) when enough questions are available.
 */
export function buildExam(
  questions: Question[],
  data: ProfileData,
  bank: BankId | null,
  count: number,
  rand: () => number = Math.random,
): Question[] {
  const pool = questions.filter((q) => !bank || q.bank === bank)
  const usedInExams = new Set(data.exams.flatMap((e) => e.results.map((r) => r.qid)))
  const weightOf = (q: Question) => (usedInExams.has(q.id) ? 0.25 : 1)

  const sample = (from: Question[], n: number): Question[] => {
    const items = [...from]
    const out: Question[] = []
    while (out.length < n && items.length) {
      const i = weightedPick(items, items.map(weightOf), rand)
      out.push(items.splice(i, 1)[0])
    }
    return out
  }

  let chosen: Question[]
  if (bank === 'kangaroo') {
    const per = Math.floor(count / 3)
    const tiers = [3, 4, 5].map((p) => pool.filter((q) => q.points === p))
    if (tiers.every((t) => t.length >= per)) {
      chosen = tiers.flatMap((t, i) => sample(t, i === 2 ? count - 2 * per : per))
    } else {
      chosen = sample(pool, count)
    }
  } else if (!bank) {
    // Mixed exams split evenly across banks so the big Kangaroo bank doesn't crowd out the
    // others; any shortfall in one bank is filled from the rest.
    const banks = [...new Set(pool.map((q) => q.bank))]
    chosen = banks.flatMap((b, i) => {
      const n = Math.floor(count / banks.length) + (i < count % banks.length ? 1 : 0)
      return sample(pool.filter((q) => q.bank === b), n)
    })
    const ids = new Set(chosen.map((q) => q.id))
    chosen.push(...sample(pool.filter((q) => !ids.has(q.id)), count - chosen.length))
  } else {
    chosen = sample(pool, count)
  }
  return chosen
    .map((q) => ({ q, k: q.difficulty + rand() * 0.5 }))
    .sort((a, b) => a.k - b.k)
    .map((x) => x.q)
}
