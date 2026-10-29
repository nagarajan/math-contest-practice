import { useCallback, useEffect, useRef, useState } from 'react'

type Point = [number, number]
type Stroke = Point[]

/** Scribbles per pad id, kept in memory so exam questions keep their work while navigating. */
const saved = new Map<string, Stroke[]>()

export function discardScratch(id: string) {
  saved.delete(id)
}

const LINE_WIDTH = 2.5

export function Scratchpad({ id }: { id: string }) {
  const wrapRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const strokes = useRef<Stroke[]>(saved.get(id) ?? [])
  const current = useRef<{ pointerId: number; stroke: Stroke } | null>(null)
  const penSeen = useRef(false)
  const [count, setCount] = useState(strokes.current.length)

  const ink = () => getComputedStyle(document.documentElement).getPropertyValue('--text').trim() || '#000'

  const redraw = useCallback(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx) return
    const dpr = window.devicePixelRatio || 1
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.strokeStyle = ctx.fillStyle = ink()
    ctx.lineWidth = LINE_WIDTH
    ctx.lineCap = ctx.lineJoin = 'round'
    for (const s of strokes.current) {
      if (s.length === 1) {
        ctx.beginPath()
        ctx.arc(s[0][0], s[0][1], LINE_WIDTH / 2, 0, Math.PI * 2)
        ctx.fill()
        continue
      }
      ctx.beginPath()
      ctx.moveTo(s[0][0], s[0][1])
      for (const [x, y] of s.slice(1)) ctx.lineTo(x, y)
      ctx.stroke()
    }
  }, [])

  useEffect(() => {
    strokes.current = saved.get(id) ?? []
    setCount(strokes.current.length)
    redraw()
  }, [id, redraw])

  useEffect(() => {
    const wrap = wrapRef.current
    const canvas = canvasRef.current
    if (!wrap || !canvas) return
    const resize = () => {
      const dpr = window.devicePixelRatio || 1
      canvas.width = Math.round(wrap.clientWidth * dpr)
      canvas.height = Math.round(wrap.clientHeight * dpr)
      redraw()
    }
    const ro = new ResizeObserver(resize)
    ro.observe(wrap)
    // Ink colour follows the light/dark theme.
    const mo = new MutationObserver(redraw)
    mo.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    })
    resize()
    return () => {
      ro.disconnect()
      mo.disconnect()
    }
  }, [redraw])

  const commit = (next: Stroke[]) => {
    strokes.current = next
    saved.set(id, next)
    setCount(next.length)
    redraw()
  }

  const pointAt = (e: { clientX: number; clientY: number }): Point => {
    const r = canvasRef.current!.getBoundingClientRect()
    return [e.clientX - r.left, e.clientY - r.top]
  }

  const onPointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (e.pointerType === 'pen') penSeen.current = true
    // Once a stylus is in use, ignore touches so a resting palm doesn't draw.
    if (e.pointerType === 'touch' && penSeen.current) return
    if (e.button !== 0 || current.current) return
    try {
      e.currentTarget.setPointerCapture(e.pointerId)
    } catch {
      // Capture only keeps strokes going outside the pad; drawing works without it.
    }
    const stroke: Stroke = [pointAt(e)]
    current.current = { pointerId: e.pointerId, stroke }
    strokes.current = [...strokes.current, stroke]
    redraw()
  }

  const onPointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const cur = current.current
    if (!cur || cur.pointerId !== e.pointerId) return
    const events = e.nativeEvent.getCoalescedEvents?.() ?? []
    for (const ev of events.length ? events : [e]) cur.stroke.push(pointAt(ev))
    redraw()
  }

  const onPointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (current.current?.pointerId !== e.pointerId) return
    current.current = null
    commit(strokes.current)
  }

  return (
    <div className="scratchpad">
      <div className="scratchpad-bar">
        <span className="muted">✏️ Scratch paper</span>
        <div className="row">
          <button className="btn small" onClick={() => commit(strokes.current.slice(0, -1))} disabled={!count}>
            ↶ Undo
          </button>
          <button className="btn small" onClick={() => commit([])} disabled={!count}>
            Clear
          </button>
        </div>
      </div>
      <div className="scratchpad-canvas" ref={wrapRef}>
        <canvas
          ref={canvasRef}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
        />
      </div>
    </div>
  )
}
