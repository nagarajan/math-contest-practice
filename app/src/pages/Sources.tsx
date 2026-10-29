import { useApp } from '../state'
import { BANK_NAMES } from '../types'

export function SourcesPage() {
  const { banks } = useApp()
  return (
    <div className="page narrow">
      <h1 className="title">Question sources</h1>
      <p className="muted">
        Every question comes from a real past competition paper that is freely available online. Solutions were written
        for this app; where the competition published an official solution, the first approach is based on it.
      </p>
      {banks.index.map((b) => (
        <section className="card" key={b.id}>
          <h2>
            {BANK_NAMES[b.id]} <span className="muted">· {b.count} questions</span>
          </h2>
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
