import { useState } from 'react'
import { useApp } from '../state'
import { gradeName, type Grade } from '../types'

const gradeRange = (gs: Grade[]) => {
  if (!gs.length) return ''
  const lo = Math.min(...gs)
  const hi = Math.max(...gs)
  if (lo >= 13) return gradeName(lo, true)
  return lo === hi ? `Gr ${lo}` : `Gr ${lo}–${Math.min(hi, 12)}${hi > 12 ? '+' : ''}`
}

export function SourcesPage() {
  const { index, grade } = useApp()
  const [onlyGrade, setOnlyGrade] = useState(true)
  const banks = index.banks
    .map((b) => ({ ...b, sources: onlyGrade ? b.sources.filter((s) => s.grades.includes(grade)) : b.sources }))
    .filter((b) => b.sources.length)
  return (
    <div className="page narrow">
      <h1 className="title">Question sources</h1>
      <p className="muted">
        Every question comes from a real past competition paper that is freely available online. Solutions were written for this app;
        where the competition published an official solution, the first approach is based on it.
      </p>
      <label className="check">
        <input type="checkbox" checked={onlyGrade} onChange={(e) => setOnlyGrade(e.target.checked)} />
        Only papers for {gradeName(grade)}
      </label>
      {banks.map((b) => (
        <section className="card" key={b.id}>
          <h2>
            {b.name} <span className="muted">· {b.sources.reduce((a, s) => a + s.count, 0)} questions</span>
          </h2>
          {b.description && <p className="muted">{b.description}</p>}
          <table className="sources-table">
            <tbody>
              {b.sources.map((s) => (
                <tr key={s.contest + s.paper + s.year}>
                  <td>{s.year ?? '—'}</td>
                  <td>
                    <a href={s.url} target="_blank" rel="noreferrer">
                      {s.contest} · {s.paper}
                    </a>
                  </td>
                  <td className="muted">{gradeRange(s.grades)}</td>
                  <td className="muted">{s.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
    </div>
  )
}
