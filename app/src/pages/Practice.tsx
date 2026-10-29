import { useEffect, useRef, useState } from 'react'
import { useApp } from '../state'
import type { Question } from '../types'
import { pickPracticeQuestion } from '../lib/selection'
import { formatAnswer, isCorrect } from '../lib/answers'
import { recordAttempt } from '../lib/storage'
import { QuestionView } from '../components/QuestionView'
import { Solutions } from '../components/Solutions'
import { formatDuration, useNow } from '../components/Timer'
import { Scratchpad, discardScratch } from '../components/Scratchpad'

export function PracticePage() {
  const { banks, data, updateData, settings } = useApp()
  const [q, setQ] = useState<Question | null>(null)
  const [value, setValue] = useState('')
  const [result, setResult] = useState<null | boolean>(null)
  const [session, setSession] = useState({ answered: 0, correct: 0 })
  const [visit, setVisit] = useState(0)
  const startedAt = useRef(Date.now())
  const now = useNow(1000)

  const next = (excludeId: string | null) => {
    const pick = pickPracticeQuestion(banks.all, data, settings.practiceBanks, excludeId)
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
        <div className="card">No questions available. Check the practice banks in Settings.</div>
      </div>
    )
  }

  const submit = () => {
    if (result !== null || !value.trim()) return
    const ok = isCorrect(q, value)
    setResult(ok)
    setSession((s) => ({
      answered: s.answered + 1,
      correct: s.correct + (ok ? 1 : 0),
    }))
    updateData((d) =>
      recordAttempt(d, {
        qid: q.id,
        bank: q.bank,
        answer: value,
        correct: ok,
        at: Date.now(),
        ms: Date.now() - startedAt.current,
        mode: 'practice',
      }),
    )
  }

  const stat = data.stats[q.id]

  return (
    <div className="page with-scratch">
      <div className="work-split">
        <div className="work-main">
          <div className="toolbar">
            <div className="muted">
              This session: {session.correct}/{session.answered} correct
              {stat && result === null ? ` · You've seen this one before (${stat.correct}/${stat.seen} right)` : ''}
            </div>
            <div className="muted">⏱ {formatDuration(now - startedAt.current)}</div>
          </div>
          <div className="card">
            <QuestionView
              q={q}
              value={value}
              onChange={setValue}
              onSubmit={submit}
              reveal={result !== null}
              disabled={result !== null}
            />
            {result === null ? (
              <div className="row">
                <button className="btn primary" onClick={submit} disabled={!value.trim()}>
                  Check answer
                </button>
                <button className="btn ghost" onClick={() => next(q.id)}>
                  Skip
                </button>
              </div>
            ) : (
              <>
                <div className={result ? 'feedback right' : 'feedback wrong'}>
                  {result ? '✅ Correct! Nice work.' : `❌ Not quite. Correct answer: ${formatAnswer(q)}`}
                  {!result ? <div className="muted">You answered: {q.type === 'mc' ? `(${value})` : value}</div> : null}
                </div>
                <Solutions q={q} />
                <div className="row">
                  <button className="btn primary" onClick={() => next(q.id)} autoFocus>
                    Next question →
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
        <Scratchpad id={`practice-${visit}`} />
      </div>
    </div>
  )
}
