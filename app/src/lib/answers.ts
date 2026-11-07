import type { BankMeta, Question } from '../types'
import { evalExpr, sameValue } from './expr'

/**
 * Parse a typed answer as a number. Accepts integers, decimals, fractions ("3/4"),
 * mixed numbers ("2 1/2"), thousands separators, a leading "$", and trailing unit words
 * ("12 cm", "64 apples"). Returns null if the input is not a number.
 */
export function parseNumber(raw: string): number | null {
  let s = raw.trim().toLowerCase()
  if (!s) return null
  s = s.replace(/^\$\s*/, '').replace(/[\u2212\u2013]/g, '-')
  s = s.replace(/(\d),(?=\d{3}\b)/g, '$1')
  const m = s.match(/^(-?\s*(?:\d+\s+\d+\s*\/\s*\d+|\d+\s*\/\s*\d+|\d*\.\d+|\d+(?:\.\d*)?))(?:\s*[^\d\s/.][^/]*)?$/)
  if (!m) return null
  const num = m[1].replace(/\s+/g, ' ').trim()
  const neg = num.startsWith('-')
  const body = num.replace(/^-\s*/, '')
  let value: number
  const mixed = body.match(/^(\d+) (\d+) ?\/ ?(\d+)$/)
  const frac = body.match(/^(\d+) ?\/ ?(\d+)$/)
  if (mixed) {
    const d = Number(mixed[3])
    if (!d) return null
    value = Number(mixed[1]) + Number(mixed[2]) / d
  } else if (frac) {
    const d = Number(frac[2])
    if (!d) return null
    value = Number(frac[1]) / d
  } else {
    value = Number(body)
  }
  if (!Number.isFinite(value)) return null
  return neg ? -value : value
}

/** Value of a typed numeric answer: plain number (with units) first, then a math expression. */
export function answerValue(raw: string, unit?: string | null): number | null {
  const n = parseNumber(raw)
  if (n !== null) return n
  let s = raw.trim()
  if (unit && s.toLowerCase().endsWith(unit.toLowerCase())) s = s.slice(0, -unit.length)
  return evalExpr(s)
}

function normText(s: string): string {
  return s
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[\u2212\u2013]/g, '-')
    .replace(/\{\s*\}/g, '∅')
    .replace(/\s*([=+*/^:<>])\s*/g, '$1')
    .replace(/[\s,;()[\]{}]+/g, ',')
    .replace(/[^a-z0-9:/.^*+\-,<>∅]+/g, '')
    .replace(/^,+|,+$/g, '')
    .replace(/\.+$/, '')
}

export function isCorrect(q: Question, given: string): boolean {
  const g = given.trim()
  if (!g || q.type === 'self') return false
  const accepted = [q.answer, ...(q.acceptedAnswers ?? [])]
  if (q.type === 'mc') return accepted.some((a) => a.toUpperCase() === g.toUpperCase())
  if (q.type === 'numeric') {
    const gv = answerValue(g, q.answerUnit)
    if (gv !== null) {
      for (const a of accepted) {
        const av = answerValue(a)
        if (av !== null && sameValue(av, gv)) return true
      }
    }
  }
  const gn = normText(g)
  if (!gn) return false
  return accepted.some((a) => normText(a) === gn)
}

/** Markdown for the correct answer. */
export function formatAnswer(q: Question): string {
  if (q.type === 'mc') {
    const c = q.choices?.find((x) => x.key === q.answer)
    return c?.text ? `(${q.answer}) ${c.text}` : `(${q.answer})`
  }
  const a = q.answerDisplay || q.answer
  return q.answerUnit ? `${a} ${q.answerUnit}` : a
}

/** One-line plain-text preview of a Markdown/KaTeX prompt for lists. */
export function plainPreview(md: string, max = 110): string {
  const s = md
    .replace(/\\(times|cdot)/g, '×')
    .replace(/\\div/g, '÷')
    .replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, '$1/$2')
    .replace(/\\[a-zA-Z]+/g, '')
    .replace(/[$*_#{}\\]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
  return s.length > max ? s.slice(0, max - 1) + '…' : s
}

/** Maximum points for a question in an exam (per-question points, e.g. Kangaroo 3/4/5, AMC 6). */
export function questionPoints(q: Question): number {
  return q.points ?? 1
}

/** Points earned in an exam, following the bank's official rules for blank and wrong answers. */
export function scoreAnswer(q: Question, given: string, bank: BankMeta | undefined): { correct: boolean; points: number } {
  if (!given.trim()) return { correct: false, points: q.blankPoints ?? bank?.blankPoints ?? 0 }
  const correct = isCorrect(q, given)
  return { correct, points: correct ? questionPoints(q) : (q.wrongPoints ?? bank?.wrongPoints ?? 0) }
}
