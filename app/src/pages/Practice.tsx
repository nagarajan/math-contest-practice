import { useEffect, useMemo, useRef, useState } from 'react'
import { useApp } from '../state'
import { gradeName, type Question } from '../types'
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
  const { banks, data, updateData, settings, grade } = useApp()
  const [q, setQ] = useState<Question | null>(null)
  const [value, setValue] = useState('')
  const [result, setResult] = useState<Result>(null)
  const [session, setSession] = useState({ answered: 0, correct: 0 })
  const [visit, setVisit] = useState(0)
  const startedAt = useRef(Date.now())
  const now = useNow(1000)

  const pool = useMemo(
    () => banks.all.filter((x) => settings.practiceSelfGraded || x.type !== 'self'),
    [banks, settings.practiceSelfGraded],
  )
  const allowed = useMemo(
    () => banks.banks.map((b) => b.id).filter((b) => !settings.practiceExcluded.includes(b)),
    [banks, settings.practiceExcluded],
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
    // Pick the first question once on mount; later picks happen on "Next".
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (!q) {
    return (
      <div className="page narrow">
        <GradeChip label="Grade" />
        <div className="card">
          No questions available for {gradeName(grade)} with the current settings. Check the practice banks in Settings.
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
