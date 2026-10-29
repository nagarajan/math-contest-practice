import { useState } from 'react'
import type { Question } from '../types'
import { Markdown } from './Markdown'

export function Solutions({ q }: { q: Question }) {
  const [tab, setTab] = useState(0)
  if (!q.solutions.length) return null
  const s = q.solutions[Math.min(tab, q.solutions.length - 1)]
  return (
    <div className="solutions">
      <div className="tabs">
        {q.solutions.map((x, i) => (
          <button key={i} className={i === tab ? 'tab active' : 'tab'} onClick={() => setTab(i)}>
            Approach {i + 1}: {x.title}
          </button>
        ))}
      </div>
      <div className="solution-body">
        <Markdown text={s.body} />
      </div>
      {q.reviewNote ? <p className="review-note">Note: {q.reviewNote}</p> : null}
    </div>
  )
}
