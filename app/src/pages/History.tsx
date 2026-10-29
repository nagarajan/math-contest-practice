import { useMemo, useState } from 'react'
import { useApp } from '../state'
import { navigate } from '../router'
import { BANK_IDS, BANK_NAMES, type BankId } from '../types'
import { formatDuration } from '../components/Timer'
import { QuestionImage, SourceTag } from '../components/QuestionView'
import { Markdown } from '../components/Markdown'
import { Solutions } from '../components/Solutions'
import { formatAnswer, plainPreview } from '../lib/answers'

export function HistoryPage() {
  const { data, banks } = useApp()
  const [tab, setTab] = useState<'exams' | 'practice' | 'topics'>('exams')
  const [open, setOpen] = useState<number | null>(null)

  const practice = useMemo(() => data.attempts.map((a, i) => ({ a, i })).filter((x) => x.a.mode === 'practice').reverse(), [data])

  const byBank = useMemo(() => {
    const r: Record<BankId, { n: number; ok: number }> = { kangaroo: { n: 0, ok: 0 }, noetic: { n: 0, ok: 0 }, moems: { n: 0, ok: 0 } }
    for (const a of data.attempts) {
      r[a.bank].n++
      if (a.correct) r[a.bank].ok++
    }
    return r
  }, [data])

  const byTopic = useMemo(() => {
    const r = new Map<string, { n: number; ok: number }>()
    for (const a of data.attempts) {
      const q = banks.byId.get(a.qid)
      for (const t of q?.topics ?? []) {
        const e = r.get(t) ?? { n: 0, ok: 0 }
        e.n++
        if (a.correct) e.ok++
        r.set(t, e)
      }
    }
    return [...r.entries()].sort((x, y) => x[1].ok / x[1].n - y[1].ok / y[1].n)
  }, [data, banks])

  return (
    <div className="page">
      <h1 className="title">History</h1>
      <div className="stat-grid">
        {BANK_IDS.map((b) => (
          <div className="stat" key={b}>
            <div className="stat-value">{byBank[b].n ? Math.round((100 * byBank[b].ok) / byBank[b].n) : 0}%</div>
            <div className="stat-label">
              {BANK_NAMES[b]} · {byBank[b].ok}/{byBank[b].n} correct
            </div>
          </div>
        ))}
      </div>
      <div className="tabs">
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

      {tab === 'exams' && (
        <div className="list">
          {!data.exams.length && <div className="card muted">No exams yet.</div>}
          {[...data.exams].reverse().map((e) => (
            <button key={e.id} className="list-row" onClick={() => navigate(`/exam/result/${e.id}`)}>
              <span>{new Date(e.finishedAt).toLocaleString()}</span>
              <span>{e.kind === 'mixed' ? 'Mixed' : BANK_NAMES[e.bank!]}</span>
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
          {practice.slice(0, 300).map(({ a, i }) => {
            const q = banks.byId.get(a.qid)
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
                      Your answer: <strong>{a.answer}</strong> · Correct answer: <strong>{formatAnswer(q)}</strong>
                    </p>
                    <Solutions q={q} />
                  </div>
                )}
              </div>
            )
          })}
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
