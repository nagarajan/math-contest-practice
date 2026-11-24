/**
 * Safe evaluator for typed math answers: numbers, + - * / ^, parentheses, implicit
 * multiplication ("3sqrt(2)", "2pi"), sqrt/cbrt/abs/ln/log/sin/cos/tan/arcsin/arccos/arctan, log bases ("log_3(9)",
 * "log2(8)", "\\log_{3} 9"), pi, e, factorial "!",
 * and simple LaTeX ("\frac{3\sqrt{2}}{4}", "2^{10}"). Returns null when it cannot parse.
 */

type Tok = { t: 'num'; v: number } | { t: 'id'; v: string } | { t: 'op'; v: string }

const FUNCS: Record<string, (x: number) => number> = {
  sqrt: Math.sqrt,
  cbrt: Math.cbrt,
  abs: Math.abs,
  ln: Math.log,
  log: Math.log10,
  sin: Math.sin,
  cos: Math.cos,
  tan: Math.tan,
  arcsin: Math.asin,
  arccos: Math.acos,
  arctan: Math.atan,
  asin: Math.asin,
  acos: Math.acos,
  atan: Math.atan,
}
const CONSTS: Record<string, number> = { pi: Math.PI, e: Math.E }

function delatex(s: string): string {
  let out = s
  for (let i = 0; i < 6; i++) {
    const before = out
    out = out
      .replace(/\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}/g, '(($1)/($2))')
      .replace(/\\sqrt\s*\[([^\]]*)\]\s*\{([^{}]*)\}/g, '(($2)^(1/($1)))')
      .replace(/\\sqrt\s*\{([^{}]*)\}/g, 'sqrt($1)')
      .replace(/\^\s*\{([^{}]*)\}/g, '^($1)')
    if (out === before) break
  }
  return out
    .replace(/\\left|\\right|\\,|\\!|\\;|\$/g, '')
    .replace(/\\(cdot|times)/g, '*')
    .replace(/\\div/g, '/')
    .replace(/\\pi/g, 'pi')
    .replace(/\\sqrt/g, 'sqrt')
    .replace(/\\(arcsin|arccos|arctan|sin|cos|tan|ln|log)/g, '$1')
    .replace(/[{}]/g, (c) => (c === '{' ? '(' : ')'))
}

function tokenize(src: string): Tok[] | null {
  const s = delatex(src)
    .toLowerCase()
    .replace(/[×·]/g, '*')
    .replace(/÷/g, '/')
    .replace(/[\u2212\u2013]/g, '-')
    .replace(/\*\*/g, '^')
    .replace(/π/g, 'pi')
    .replace(/√/g, 'sqrt')
  const out: Tok[] = []
  let i = 0
  while (i < s.length) {
    const c = s[i]
    if (/\s/.test(c)) {
      i++
      continue
    }
    const num = s.slice(i).match(/^(\d+\.?\d*|\.\d+)/)
    if (num) {
      // "12 3" is a typo, not 12 times 3.
      if (out[out.length - 1]?.t === 'num') return null
      out.push({ t: 'num', v: Number(num[1]) })
      i += num[1].length
      continue
    }
    const logBase = s.slice(i).match(/^log(?:_\(?(\d+\.?\d*)\)?|(\d+\.?\d*)(?=\s*\())/)
    if (logBase) {
      out.push({ t: 'id', v: `log@${logBase[1] ?? logBase[2]}` })
      i += logBase[0].length
      continue
    }
    const id = s.slice(i).match(/^[a-z]+/)
    if (id) {
      let w = id[0]
      // Split runs like "sqrtpi" or "pie" into known names, longest first.
      while (w) {
        const name = [...Object.keys(FUNCS), ...Object.keys(CONSTS)].sort((a, b) => b.length - a.length).find((n) => w.startsWith(n))
        if (!name) return null
        out.push({ t: 'id', v: name })
        w = w.slice(name.length)
      }
      i += id[0].length
      continue
    }
    if ('+-*/^()!'.includes(c)) {
      out.push({ t: 'op', v: c })
      i++
      continue
    }
    return null
  }
  return out
}

function factorial(n: number): number {
  if (!Number.isInteger(n) || n < 0 || n > 170) return NaN
  let r = 1
  for (let k = 2; k <= n; k++) r *= k
  return r
}

export function evalExpr(src: string): number | null {
  const parsed = tokenize(src)
  if (!parsed || !parsed.length) return null
  const toks: Tok[] = parsed
  let p = 0
  const peek = () => toks[p]
  const isOp = (v: string) => peek()?.t === 'op' && peek()!.v === v
  const startsPrimary = () => {
    const k = peek()
    return !!k && (k.t === 'num' || k.t === 'id' || (k.t === 'op' && k.v === '('))
  }

  function expr(): number {
    let v = term()
    while (isOp('+') || isOp('-')) {
      const op = toks[p++].v
      const r = term()
      v = op === '+' ? v + r : v - r
    }
    return v
  }
  function term(): number {
    let v = unary()
    for (;;) {
      if (isOp('*') || isOp('/')) {
        const op = toks[p++].v
        const r = unary()
        v = op === '*' ? v * r : v / r
      } else if (startsPrimary()) {
        v *= power()
      } else return v
    }
  }
  function unary(): number {
    if (isOp('-')) {
      p++
      return -unary()
    }
    if (isOp('+')) {
      p++
      return unary()
    }
    return power()
  }
  function power(): number {
    const base = postfix()
    if (isOp('^')) {
      p++
      return Math.pow(base, unary())
    }
    return base
  }
  function postfix(): number {
    let v = primary()
    while (isOp('!')) {
      p++
      v = factorial(v)
    }
    return v
  }
  function primary(): number {
    const k = toks[p++]
    if (!k) throw new Error('end')
    if (k.t === 'num') return k.v
    if (k.t === 'id') {
      if (k.v in CONSTS) return CONSTS[k.v]
      if (k.v.startsWith('log@')) return Math.log(power()) / Math.log(Number(k.v.slice(4)))
      const f = FUNCS[k.v]
      // sqrt2, sqrt 2 and sqrt(2) all work; the argument binds tighter than * and /.
      return f(power())
    }
    if (k.v === '(') {
      const v = expr()
      if (!isOp(')')) throw new Error('paren')
      p++
      return v
    }
    throw new Error('unexpected')
  }

  try {
    const v = expr()
    if (p !== toks.length || !Number.isFinite(v)) return null
    return v
  } catch {
    return null
  }
}

export function sameValue(a: number, b: number): boolean {
  if (a === 0 || b === 0) return Math.abs(a + b) < 1e-14
  return Math.abs(a - b) <= 1e-9 * Math.max(Math.abs(a), Math.abs(b))
}
