import { useState } from 'react'
import type { Question } from '../types'
import { BANK_NAMES } from '../types'
import { assetUrl } from '../lib/banks'
import { Markdown } from './Markdown'

export function SourceTag({ q }: { q: Question }) {
  const num = q.source.number != null ? ` · Q${q.source.number}` : ''
  return (
    <div className="source-tag">
      <span className={`bank-pill bank-${q.bank}`}>{BANK_NAMES[q.bank]}</span>
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
      ) : (
        <div className="answer-row">
          <input
            className="answer-input"
            inputMode={q.type === 'numeric' ? 'decimal' : 'text'}
            placeholder={q.type === 'numeric' ? 'Your answer (e.g. 42, 3/4, 2.5)' : 'Your answer'}
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
