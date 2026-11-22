import { useEffect, useState } from 'react'
import type { Question, Solution } from '../types'
import { loadSolutions } from '../lib/banks'
import { Markdown } from './Markdown'

export function Solutions({ q }: { q: Question }) {
  const [tab, setTab] = useState(0)
  const [state, setState] = useState<{ id: string; sols: Solution[] | null; error?: boolean }>({ id: q.id, sols: q.solutions ?? null })

  useEffect(() => {
    let live = true
    setTab(0)
    setState({ id: q.id, sols: q.solutions ?? null })
    loadSolutions(q)
      .then((sols) => live && setState({ id: q.id, sols }))
      .catch(() => live && setState({ id: q.id, sols: null, error: true }))
    return () => {
      live = false
    }
  }, [q])

  const note = q.reviewNote ? <p className="review-note">Note: {q.reviewNote}</p> : null
  if (state.id !== q.id || (!state.sols && !state.error)) return <div className="solutions muted">Loading solution…</div>
  if (state.error) return <div className="solutions muted">Could not load the solution. Check the connection and try again.</div>
  const sols = state.sols ?? []
  if (!sols.length) return note
  const s = sols[Math.min(tab, sols.length - 1)]
  return (
    <div className="solutions">
      <div className="tabs">
        {sols.map((x, i) => (
          <button key={i} className={i === tab ? 'tab active' : 'tab'} onClick={() => setTab(i)}>
            Approach {i + 1}: {x.title}
          </button>
        ))}
      </div>
      <div className="solution-body">
        <Markdown text={s.body} />
      </div>
      {note}
    </div>
  )
}
