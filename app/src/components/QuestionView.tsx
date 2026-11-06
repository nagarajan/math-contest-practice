import { useState } from 'react'
import type { BankId, Question } from '../types'
import { assetUrl, bankMeta } from '../lib/banks'
import { useApp } from '../state'
import { Markdown } from './Markdown'

export function BankPill({ bank }: { bank: BankId }) {
  const { index } = useApp()
  const meta = bankMeta(index, bank)
  return (
    <span className="bank-pill" style={{ background: meta?.color ?? '#64748b' }}>
      {meta?.name ?? bank}
    </span>
  )
}

export function SourceTag({ q }: { q: Question }) {
  const num = q.source.number != null ? ` · ${/^\d+$/.test(String(q.source.number)) ? 'Q' : ''}${q.source.number}` : ''
  return (
    <div className="source-tag">
      <BankPill bank={q.bank} />
      <span className="muted">
        {q.source.contest} · {q.source.paper}
        {!q.source.year || q.source.paper.includes(String(q.source.year)) ? '' : ` · ${q.source.year}`}
        {num}
      </span>
      {q.points ? <span className="points">{q.points} pts</span> : null}
      {q.timeMinutes ? <span className="points">{q.timeMinutes} min</span> : null}
    </div>
  )
}

export function QuestionImage({ src }: { src: string }) {
  const [zoom, setZoom] = useState(false)
  return (
    <>
      <img className="q-image" src={assetUrl(src)} alt="Figure for the question" onClick={() => setZoom(true)} />
      {zoom && (
        <div className="zoom-overlay" onClick={() => setZoom(false)}>
          <img src={assetUrl(src)} alt="Figure enlarged" />
        </div>
      )}
    </>
  )
}

interface Props {
  q: Question
  value: string
  onChange: (v: string) => void
  onSubmit?: () => void
  /** After answering in practice: highlight the correct and chosen options. */
  reveal?: boolean
  disabled?: boolean
}

export function QuestionView({ q, value, onChange, onSubmit, reveal, disabled }: Props) {
  return (
    <div className="question">
      <SourceTag q={q} />
      <Markdown text={q.prompt} />
      {q.image && <QuestionImage src={q.image} />}
      {q.type === 'mc' && q.choices ? (
        <div
          className={`choices ${q.choices.every((c) => !c.text) ? 'choices-compact' : q.choices.some((c) => c.text.length > 24) ? 'choices-long' : ''}`}
        >
          {q.choices.map((c) => {
            const cls = ['choice']
            if (value === c.key) cls.push('selected')
            const isRight = c.key === q.answer || !!q.acceptedAnswers?.includes(c.key)
            if (reveal && isRight) cls.push('right')
            if (reveal && value === c.key && !isRight) cls.push('wrong')
            return (
              <button
                key={c.key}
                className={cls.join(' ')}
                disabled={disabled}
                onClick={() => onChange(value === c.key ? '' : c.key)}
              >
                <span className="choice-key">{c.key}</span>
                {c.text ? <Markdown text={c.text} inline /> : null}
                {c.image ? <img src={assetUrl(c.image)} alt={`Choice ${c.key}`} /> : null}
              </button>
            )
          })}
        </div>
      ) : q.type === 'self' ? (
        <p className="self-note muted">Work it out on the scratch paper, then check your answer against the solution.</p>
      ) : (
        <div className="answer-row">
          <input
            className="answer-input"
            inputMode={q.type === 'numeric' ? 'decimal' : 'text'}
            placeholder={
              q.type !== 'numeric'
                ? 'Your answer'
                : q.grades.every((g) => g <= 6)
                  ? 'Your answer (e.g. 42, 3/4, 2.5)'
                  : 'Your answer (e.g. 42, 3/4, 2sqrt(3), pi/6, 2^10)'
            }
            value={value}
            disabled={disabled}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && onSubmit) onSubmit()
            }}
            autoFocus
          />
          {q.answerUnit ? <span className="unit">{q.answerUnit}</span> : null}
        </div>
      )}
    </div>
  )
}
