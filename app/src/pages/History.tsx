import { useMemo, useState } from 'react'
import { useApp } from '../state'
import { navigate } from '../router'
import { formatDuration } from '../components/Timer'
import { QuestionImage, SourceTag } from '../components/QuestionView'
import { Markdown } from '../components/Markdown'
import { Solutions } from '../components/Solutions'
import { formatAnswer, plainPreview } from '../lib/answers'
import { useLookup } from '../lib/useLookup'
import { examTitle } from '../lib/banks'
import { BankPill } from '../components/QuestionView'
import { gradeName, NO_FOCUS } from '../types'

export function HistoryPage() {
  const { data, index, banks, grade, settings, setSettings } = useApp()
  const [tab, setTab] = useState<'progress' | 'exams' | 'practice' | 'topics'>('progress')
  const [open, setOpen] = useState<number | null>(null)
  const [limit, setLimit] = useState(50)
  const practice = useMemo(() => data.attempts.map((a, i) => ({ a, i })).filter((x) => x.a.mode === 'practice').reverse(), [data])
  const recent = practice.slice(0, limit)
  const lookup = useLookup(
    data.attempts.map((a) => a.grade),
    tab === 'practice' ? recent.map((x) => x.a.qid) : [],
  )

  const byBank = useMemo(() => {
    const r = new Map<string, { n: number; ok: number }>()
    for (const a of data.attempts) {
      const e = r.get(a.bank) ?? { n: 0, ok: 0 }
      e.n++
      if (a.correct) e.ok++
      r.set(a.bank, e)
    }
    return index.banks.filter((b) => r.has(b.id)).map((b) => ({ id: b.id, name: b.name, ...r.get(b.id)! }))
  }, [data, index])

  const progress = useMemo(
    () =>
      banks.banks
        .map((b) => {
          const qs = banks.all.filter((q) => q.bank === b.id)
          const seen = qs.filter((q) => data.stats[q.id]?.seen)
          const right = seen.filter((q) => data.stats[q.id].lastCorrect).length
          return { b, total: qs.length, seen: seen.length, right, revisit: seen.length - right }
        })
        .filter((x) => x.total)
        .sort((x, y) => y.seen / y.total - x.seen / x.total || y.total - x.total),
    [banks, data],
  )

  const practiseBank = (bank: string) => {
    setSettings({ ...settings, practiceFocus: { ...NO_FOCUS, bank } })
    navigate('/practice')
  }

  const byTopic = useMemo(() => {
    const r = new Map<string, { n: number; ok: number }>()
    for (const a of data.attempts) {
      const q = lookup.get(a.qid)
      for (const t of q?.topics ?? []) {
        const e = r.get(t) ?? { n: 0, ok: 0 }
        e.n++
        if (a.correct) e.ok++
        r.set(t, e)
      }
    }
    return [...r.entries()].sort((x, y) => x[1].ok / x[1].n - y[1].ok / y[1].n)
  }, [data, lookup])

  return (
    <div className="page">
      <h1 className="title">History</h1>
      <div className="stat-grid">
        {!byBank.length && <div className="muted">No answers yet.</div>}
        {byBank.map((s) => (
          <div className="stat" key={s.id}>
            <div className="stat-value">{s.n ? Math.round((100 * s.ok) / s.n) : 0}%</div>
            <div className="stat-label">
              {s.name} · {s.ok}/{s.n} correct
            </div>
          </div>
        ))}
      </div>
      <div className="tabs">
        <button className={tab === 'progress' ? 'tab active' : 'tab'} onClick={() => setTab('progress')}>
          By competition
        </button>
        <button className={tab === 'exams' ? 'tab active' : 'tab'} onClick={() => setTab('exams')}>
          Exams ({data.exams.length})
        </button>
        <button className={tab === 'practice' ? 'tab active' : 'tab'} onClick={() => setTab('practice')}>
          Practice ({practice.length})
        </button>
        <button className={tab === 'topics' ? 'tab active' : 'tab'} onClick={() => setTab('topics')}>
          By topic
        </button>
      </div>

      {tab === 'progress' && (
        <div className="list">
          <div className="muted small">
            Questions seen so far in each competition for {gradeName(grade)}. "Right" counts questions whose last answer was correct.
          </div>
          {progress.map(({ b, total, seen, right, revisit }) => (
            <div key={b.id} className="progress-row">
              <BankPill bank={b.id} />
              <div className="bar" title={`${seen} of ${total} seen`}>
                <div className="bar-fill" style={{ width: `${(100 * seen) / total}%` }} />
              </div>
              <span className="muted small progress-nums">
                {seen}/{total} seen{seen ? ` · ${right} right · ${revisit} to revisit` : ''}
              </span>
              <button className="btn small" onClick={() => practiseBank(b.id)}>
                Practice
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === 'exams' && (
        <div className="list">
          {!data.exams.length && <div className="card muted">No exams yet.</div>}
          {[...data.exams].reverse().map((e) => (
            <button key={e.id} className="list-row" onClick={() => navigate(`/exam/result/${e.id}`)}>
              <span>{new Date(e.finishedAt).toLocaleString()}</span>
              <span>{examTitle(index, e)}</span>
              <span>
                <strong>
                  {e.score}/{e.maxScore}
                </strong>{' '}
                · {e.correctCount}/{e.results.length} correct
              </span>
              <span>⏱ {formatDuration(e.elapsedMs)}</span>
            </button>
          ))}
        </div>
      )}

      {tab === 'practice' && (
        <div className="list">
          {!practice.length && <div className="card muted">No practice questions yet.</div>}
          {recent.map(({ a, i }) => {
            const q = lookup.get(a.qid)
            if (!q) return null
            return (
              <div key={i} className={`review-item ${a.correct ? 'right' : 'wrong'}`}>
                <button className="review-head" onClick={() => setOpen(open === i ? null : i)}>
                  <span className="review-mark">{a.correct ? '✅' : '❌'}</span>
                  <span className="review-text">{plainPreview(q.prompt, 100)}</span>
                  <span className="muted small">{new Date(a.at).toLocaleString()}</span>
                </button>
                {open === i && (
                  <div className="review-body">
                    <SourceTag q={q} />
                    <Markdown text={q.prompt} />
                    {q.image && <QuestionImage src={q.image} />}
                    <p>
                      Your answer: <strong>{a.selfGraded ? (a.correct ? 'solved (self-checked)' : 'not yet (self-checked)') : a.answer}</strong> ·
                      Correct answer:{' '}
                      <strong>
                        <Markdown text={formatAnswer(q)} inline />
                      </strong>
                    </p>
                    <Solutions q={q} />
                  </div>
                )}
              </div>
            )
          })}
          {practice.length > limit && (
            <button className="btn ghost" onClick={() => setLimit(limit + 50)}>
              Show more
            </button>
          )}
        </div>
      )}

      {tab === 'topics' && (
        <div className="list">
          {!byTopic.length && <div className="card muted">Answer some questions to see topic stats.</div>}
          {byTopic.map(([t, s]) => (
            <div key={t} className="topic-row">
              <span className="topic-name">{t.replace(/-/g, ' ')}</span>
              <div className="bar">
                <div className="bar-fill" style={{ width: `${(100 * s.ok) / s.n}%` }} />
              </div>
              <span className="muted">
                {s.ok}/{s.n}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
