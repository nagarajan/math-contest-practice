import { useEffect, useState } from 'react'

export function formatDuration(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return h ? `${h}:${mm}:${ss}` : `${mm}:${ss}`
}

/** Re-renders every half second and reports the current time. */
export function useNow(intervalMs = 500): number {
  const [now, setNow] = useState(Date.now())
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), intervalMs)
    return () => clearInterval(t)
  }, [intervalMs])
  return now
}

export function Clock({ elapsedMs, limitMin }: { elapsedMs: number; limitMin: number | null }) {
  const remaining = limitMin ? limitMin * 60000 - elapsedMs : null
  const low = remaining !== null && remaining < 5 * 60000
  return (
    <div className={`clock ${low ? 'clock-low' : ''}`} aria-live="off">
      <span className="clock-label">Elapsed</span>
      <span className="clock-value">{formatDuration(elapsedMs)}</span>
      {remaining !== null && (
        <>
          <span className="clock-label">Left</span>
          <span className="clock-value">{formatDuration(remaining)}</span>
        </>
      )}
    </div>
  )
}
