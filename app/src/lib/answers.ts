import type { Question } from '../types'

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

function normText(s: string): string {
  return s
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9:/.]+/g, '')
    .replace(/\.+$/, '')
}

export function isCorrect(q: Question, given: string): boolean {
  const g = given.trim()
  if (!g) return false
  const accepted = [q.answer, ...(q.acceptedAnswers ?? [])]
  if (q.type === 'mc') return accepted.some((a) => a.toUpperCase() === g.toUpperCase())
  if (q.type === 'numeric') {
    const gv = parseNumber(g)
    if (gv !== null) {
      for (const a of accepted) {
        const av = parseNumber(a)
        if (av !== null && Math.abs(av - gv) < 1e-9) return true
      }
    }
  }
  const gn = normText(g)
  return accepted.some((a) => normText(a) === gn)
}

export function formatAnswer(q: Question): string {
  if (q.type === 'mc') {
    const c = q.choices?.find((x) => x.key === q.answer)
    return c?.text ? `(${q.answer}) ${c.text}` : `(${q.answer})`
  }
  return q.answerUnit ? `${q.answer} ${q.answerUnit}` : q.answer
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

/** Points awarded for a question in an exam, following each contest's official scoring. */
export function questionPoints(q: Question): number {
  if (q.bank === 'kangaroo') return q.points ?? 3
  return 1
}
