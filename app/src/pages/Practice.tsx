import { useEffect, useMemo, useRef, useState } from 'react'
import { useApp } from '../state'
import { gradeName, NO_FOCUS, type PracticeFocus, type Question } from '../types'
import { pickPracticeQuestion } from '../lib/selection'
import { formatAnswer, isCorrect } from '../lib/answers'
import { recordAttempt } from '../lib/storage'
import { QuestionView } from '../components/QuestionView'
import { Solutions } from '../components/Solutions'
import { Markdown } from '../components/Markdown'
import { formatDuration, useNow } from '../components/Timer'
import { Scratchpad, discardScratch } from '../components/Scratchpad'
import { GradeChip } from './Profiles'

/** Practice result: null while answering; "shown" = self-graded solution revealed, not yet marked. */
type Result = null | 'shown' | boolean

export function PracticePage() {
  const { banks, data, updateData, settings, setSettings, grade } = useApp()
  const [q, setQ] = useState<Question | null>(null)
  const [value, setValue] = useState('')
  const [result, setResult] = useState<Result>(null)
  const [session, setSession] = useState({ answered: 0, correct: 0 })
  const [visit, setVisit] = useState(0)
  const startedAt = useRef(Date.now())
  const now = useNow(1000)

  const base = useMemo(
    () => banks.all.filter((x) => settings.practiceSelfGraded || x.type !== 'self'),
    [banks, settings.practiceSelfGraded],
  )
  const focus = settings.practiceFocus ?? NO_FOCUS
  const focused = !!(focus.bank || focus.topic || focus.difficulty)
  const setFocus = (patch: Partial<PracticeFocus>) => setSettings({ ...settings, practiceFocus: { ...focus, ...patch } })
  const pool = useMemo(
    () =>
      base.filter(
        (x) =>
          (!focus.bank || x.bank === focus.bank) &&
          (!focus.topic || x.topics.includes(focus.topic)) &&
          (!focus.difficulty || x.difficulty === focus.difficulty),
      ),
    [base, focus.bank, focus.topic, focus.difficulty],
  )
  const allowed = useMemo(
    () => (focus.bank ? [focus.bank] : banks.banks.map((b) => b.id).filter((b) => !settings.practiceExcluded.includes(b))),
    [banks, settings.practiceExcluded, focus.bank],
  )
  const next = (excludeId: string | null) => {
    const pick = pickPracticeQuestion(pool, data, allowed, excludeId)
    discardScratch(`practice-${visit}`)
    setVisit((v) => v + 1)
    setQ(pick)
    setValue('')
    setResult(null)
    startedAt.current = Date.now()
  }

  useEffect(() => {
    next(null)
    // Pick a question on mount and whenever the focus changes; later picks happen on "Next".
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus.bank, focus.topic, focus.difficulty])

  const filters = <PracticeFilters base={base} focus={focus} setFocus={setFocus} matching={focused ? pool.length : null} />

  if (!q) {
    return (
      <div className="page narrow">
        <GradeChip label="Grade" />
        {filters}
        <div className="card">
          No questions available for {gradeName(grade)} with the current filters and settings.{' '}
          {focused && (
            <button className="link" onClick={() => setSettings({ ...settings, practiceFocus: NO_FOCUS })}>
              Clear filters
            </button>
          )}
        </div>
      </div>
    )
  }

  const record = (ok: boolean, answer: string) => {
    setResult(ok)
    setSession((s) => ({ answered: s.answered + 1, correct: s.correct + (ok ? 1 : 0) }))
    updateData((d) =>
      recordAttempt(d, {
        qid: q.id,
        bank: q.bank,
        answer,
        correct: ok,
        at: Date.now(),
        ms: Date.now() - startedAt.current,
        mode: 'practice',
        grade,
        ...(q.type === 'self' ? { selfGraded: true } : {}),
      }),
    )
  }

  const submit = () => {
    if (result !== null || !value.trim() || q.type === 'self') return
    record(isCorrect(q, value), value)
  }

  const stat = data.stats[q.id]
  const answered = result !== null

  return (
    <div className="page with-scratch">
      <div className="work-split">
        <div className="work-main">
          {filters}
          <div className="toolbar">
            <GradeChip label="Grade" />
            <div className="muted">
              This session: {session.correct}/{session.answered} correct
              {stat && !answered ? ` · You've seen this one before (${stat.correct}/${stat.seen} right)` : ''}
            </div>
            <div className="muted">⏱ {formatDuration(now - startedAt.current)}</div>
          </div>
          <div className="card">
            <QuestionView q={q} value={value} onChange={setValue} onSubmit={submit} reveal={answered} disabled={answered} />
            {!answered ? (
              <div className="row">
                {q.type === 'self' ? (
                  <button className="btn primary" onClick={() => setResult('shown')}>
                    Show solution
                  </button>
                ) : (
                  <button className="btn primary" onClick={submit} disabled={!value.trim()}>
                    Check answer
                  </button>
                )}
                <button className="btn ghost" onClick={() => next(q.id)}>
                  Skip
                </button>
              </div>
            ) : (
              <>
                {q.type === 'self' ? (
                  <div className="feedback">
                    <div>
                      <strong>Answer:</strong> <Markdown text={formatAnswer(q)} inline />
                    </div>
                    {result === 'shown' ? (
                      <div className="self-grade">
                        <span className="muted">Compare with the solution below. Did you solve it?</span>
                        <button className="btn primary" onClick={() => record(true, '(self-graded)')}>
                          ✅ I got it
                        </button>
                        <button className="btn" onClick={() => record(false, '(self-graded)')}>
                          ❌ Not yet
                        </button>
                      </div>
                    ) : (
                      <div className="muted">{result ? 'Marked as solved.' : 'Marked to revisit — it will come back later.'}</div>
                    )}
                  </div>
                ) : (
                  <div className={result ? 'feedback right' : 'feedback wrong'}>
                    {result ? (
                      '✅ Correct! Nice work.'
                    ) : (
                      <>
                        ❌ Not quite. Correct answer: <Markdown text={formatAnswer(q)} inline />
                      </>
                    )}
                    {!result ? <div className="muted">You answered: {q.type === 'mc' ? `(${value})` : value}</div> : null}
                  </div>
                )}
                <Solutions q={q} />
                {result !== 'shown' && (
                  <div className="row">
                    <button className="btn primary" onClick={() => next(q.id)} autoFocus>
                      Next question →
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
        <Scratchpad id={`practice-${visit}`} />
      </div>
    </div>
  )
}

const DIFFICULTY = { 1: 'Easy', 2: 'Medium', 3: 'Hard' } as const

function PracticeFilters({
  base,
  focus,
  setFocus,
  matching,
}: {
  base: Question[]
  focus: PracticeFocus
  setFocus: (patch: Partial<PracticeFocus>) => void
  matching: number | null
}) {
  const { banks } = useApp()
  const count = (pred: (q: Question) => boolean) => base.filter(pred).length
  const inBank = (q: Question) => !focus.bank || q.bank === focus.bank
  const topics = useMemo(() => {
    const c = new Map<string, number>()
    for (const q of base) if (inBank(q)) for (const t of q.topics) c.set(t, (c.get(t) ?? 0) + 1)
    return [...c.entries()].sort((a, b) => b[1] - a[1])
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [base, focus.bank])

  return (
    <div className="practice-filters">
      <label>
        <span className="muted">Competition</span>
        <select value={focus.bank ?? ''} onChange={(e) => setFocus({ bank: e.target.value || null, topic: null })}>
          <option value="">All</option>
          {banks.banks
            .map((b) => ({ b, n: count((q) => q.bank === b.id) }))
            .filter((x) => x.n)
            .map(({ b, n }) => (
              <option key={b.id} value={b.id}>
                {b.name} ({n})
              </option>
            ))}
        </select>
      </label>
      <label>
        <span className="muted">Topic</span>
        <select value={focus.topic ?? ''} onChange={(e) => setFocus({ topic: e.target.value || null })}>
          <option value="">All</option>
          {topics.map(([t, n]) => (
            <option key={t} value={t}>
              {t.replace(/-/g, ' ')} ({n})
            </option>
          ))}
        </select>
      </label>
      <label>
        <span className="muted">Difficulty</span>
        <select
          value={focus.difficulty ?? ''}
          onChange={(e) => setFocus({ difficulty: e.target.value ? (Number(e.target.value) as 1 | 2 | 3) : null })}
        >
          <option value="">Any</option>
          {([1, 2, 3] as const).map((d) => (
            <option key={d} value={d}>
              {DIFFICULTY[d]}
            </option>
          ))}
        </select>
      </label>
      {matching !== null && <span className="muted small">{matching} matching questions</span>}
    </div>
  )
}
