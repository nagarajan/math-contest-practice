import { useEffect, useMemo, useRef, useState } from 'react'
import { useApp } from '../state'
import { navigate } from '../router'
import { BANK_IDS, BANK_NAMES, type Attempt, type BankId, type ExamKind, type ExamRecord, type Question } from '../types'
import { buildExam } from '../lib/selection'
import { formatAnswer, isCorrect, plainPreview, questionPoints } from '../lib/answers'
import { newId, recordExam } from '../lib/storage'
import { QuestionView, SourceTag, QuestionImage } from '../components/QuestionView'
import { Solutions } from '../components/Solutions'
import { Clock, formatDuration, useNow } from '../components/Timer'
import { Markdown } from '../components/Markdown'
import { Scratchpad, discardScratch } from '../components/Scratchpad'

const SCORING_NOTE: Record<BankId, string> = {
  kangaroo: 'Kangaroo questions are worth 3, 4 or 5 points (no penalty for wrong answers).',
  noetic: 'Noetic questions are worth 1 point each.',
  moems: 'Math Olympiad (MOEMS) questions are worth 1 point each.',
}

export function ExamSetupPage({ kind }: { kind: ExamKind }) {
  const { banks, data, updateData, settings } = useApp()
  const [bank, setBank] = useState<BankId>('kangaroo')
  const counts = useMemo(() => {
    const c: Record<BankId, number> = { kangaroo: 0, noetic: 0, moems: 0 }
    for (const q of banks.all) c[q.bank]++
    return c
  }, [banks])

  const available = kind === 'mixed' ? banks.all.length : counts[bank]
  const n = Math.min(settings.examQuestionCount, available)

  const start = () => {
    const qs = buildExam(banks.all, data, kind === 'focused' ? bank : null, settings.examQuestionCount)
    const now = Date.now()
    updateData((d) => ({
      ...d,
      examInProgress: {
        id: newId(),
        kind,
        bank: kind === 'focused' ? bank : null,
        qids: qs.map((q) => q.id),
        answers: {},
        flagged: [],
        current: 0,
        startedAt: now,
        elapsedBeforeMs: 0,
        resumedAt: now,
        timeLimitMin: settings.examTimeLimitMin,
      },
    }))
    navigate('/exam/run')
  }

  if (data.examInProgress) {
    return (
      <div className="page narrow">
        <div className="card">
          <p>You already have an exam in progress.</p>
          <button className="btn primary" onClick={() => navigate('/exam/run')}>
            Resume it
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="page narrow">
      <h1 className="title">{kind === 'mixed' ? 'Mixed exam' : 'Focused exam'}</h1>
      <div className="card">
        {kind === 'focused' && (
          <>
            <h2>Choose a competition</h2>
            <div className="bank-choices">
              {BANK_IDS.map((b) => (
                <button
                  key={b}
                  className={b === bank ? 'bank-choice selected' : 'bank-choice'}
                  onClick={() => setBank(b)}
                  disabled={!counts[b]}
                >
                  <span className={`bank-pill bank-${b}`}>{BANK_NAMES[b]}</span>
                  <span className="muted">{counts[b]} questions</span>
                </button>
              ))}
            </div>
          </>
        )}
        <ul className="exam-facts">
          <li>
            <strong>{n} questions</strong>
            {n < settings.examQuestionCount ? ` (only ${available} available in this bank)` : ''}, ordered from easier to harder.
          </li>
          <li>
            {settings.examTimeLimitMin
              ? `Time limit: ${settings.examTimeLimitMin} minutes. The exam is submitted automatically when time runs out.`
              : 'No time limit — the clock shows how long you take.'}
          </li>
          <li>You can move between questions and change answers until you submit.</li>
          <li>{kind === 'mixed' ? BANK_IDS.map((b) => SCORING_NOTE[b]).join(' ') : SCORING_NOTE[bank]}</li>
        </ul>
        <button className="btn primary big" onClick={start} disabled={!n}>
          Start exam
        </button>
      </div>
    </div>
  )
}

export function ExamRunPage() {
  const { banks, data, updateData } = useApp()
  const exam = data.examInProgress
  const now = useNow(500)
  const [confirming, setConfirming] = useState(false)
  const finishing = useRef(false)

  const questions = useMemo(
    () => (exam ? exam.qids.map((id) => banks.byId.get(id)).filter((q): q is Question => !!q) : []),
    [exam, banks],
  )

  // The clock only runs while the exam is on screen: elapsed time is banked when leaving
  // (tab hidden, reload, navigating away) and the clock restarts from "now" on return.
  useEffect(() => {
    if (!exam) return
    updateData((d) =>
      d.examInProgress
        ? {
            ...d,
            examInProgress: { ...d.examInProgress, resumedAt: Date.now() },
          }
        : d,
    )
    const persist = () =>
      updateData((d) =>
        d.examInProgress
          ? {
              ...d,
              examInProgress: {
                ...d.examInProgress,
                elapsedBeforeMs: d.examInProgress.elapsedBeforeMs + (Date.now() - d.examInProgress.resumedAt),
                resumedAt: Date.now(),
              },
            }
          : d,
      )
    const t = setInterval(persist, 15000)
    const onVisibility = () => {
      if (document.visibilityState === 'hidden') persist()
      else
        updateData((d) =>
          d.examInProgress
            ? {
                ...d,
                examInProgress: { ...d.examInProgress, resumedAt: Date.now() },
              }
            : d,
        )
    }
    document.addEventListener('visibilitychange', onVisibility)
    window.addEventListener('beforeunload', persist)
    return () => {
      clearInterval(t)
      document.removeEventListener('visibilitychange', onVisibility)
      window.removeEventListener('beforeunload', persist)
      if (!finishing.current) persist()
    }
    // Only re-bind when a different exam starts.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [exam?.id])

  const elapsed = exam ? exam.elapsedBeforeMs + (now - exam.resumedAt) : 0

  const finish = (timedOut: boolean) => {
    if (!exam || finishing.current) return
    finishing.current = true
    for (const qid of exam.qids) discardScratch(`exam-${exam.id}-${qid}`)
    const finishedAt = Date.now()
    const elapsedMs = exam.elapsedBeforeMs + (finishedAt - exam.resumedAt)
    const results = questions.map((q) => {
      const answer = exam.answers[q.id] ?? ''
      const correct = isCorrect(q, answer)
      const maxPoints = questionPoints(q)
      return {
        qid: q.id,
        answer,
        correct,
        points: correct ? maxPoints : 0,
        maxPoints,
      }
    })
    const record: ExamRecord = {
      id: exam.id,
      kind: exam.kind,
      bank: exam.bank,
      startedAt: exam.startedAt,
      finishedAt,
      elapsedMs: exam.timeLimitMin ? Math.min(elapsedMs, exam.timeLimitMin * 60000) : elapsedMs,
      timeLimitMin: exam.timeLimitMin,
      timedOut,
      results,
      score: results.reduce((a, r) => a + r.points, 0),
      maxScore: results.reduce((a, r) => a + r.maxPoints, 0),
      correctCount: results.filter((r) => r.correct).length,
    }
    const attempts: Attempt[] = results.map((r) => ({
      qid: r.qid,
      bank: banks.byId.get(r.qid)!.bank,
      answer: r.answer,
      correct: r.correct,
      at: finishedAt,
      ms: 0,
      mode: 'exam',
      examId: exam.id,
    }))
    updateData((d) => recordExam(d, record, attempts))
    navigate(`/exam/result/${exam.id}`)
  }

  useEffect(() => {
    if (exam?.timeLimitMin && elapsed >= exam.timeLimitMin * 60000) finish(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [elapsed])

  if (!exam) {
    return (
      <div className="page narrow">
        <div className="card">
          No exam in progress.{' '}
          <button className="btn" onClick={() => navigate('/')}>
            Home
          </button>
        </div>
      </div>
    )
  }

  const idx = Math.min(exam.current, questions.length - 1)
  const q = questions[idx]
  const setCurrent = (i: number) =>
    updateData((d) => (d.examInProgress ? { ...d, examInProgress: { ...d.examInProgress, current: i } } : d))
  const setAnswer = (v: string) =>
    updateData((d) => {
      if (!d.examInProgress) return d
      const answers = { ...d.examInProgress.answers }
      if (v.trim()) answers[q.id] = v
      else delete answers[q.id]
      return { ...d, examInProgress: { ...d.examInProgress, answers } }
    })
  const toggleFlag = () =>
    updateData((d) => {
      if (!d.examInProgress) return d
      const f = d.examInProgress.flagged
      return {
        ...d,
        examInProgress: {
          ...d.examInProgress,
          flagged: f.includes(q.id) ? f.filter((x) => x !== q.id) : [...f, q.id],
        },
      }
    })
  const answeredCount = Object.keys(exam.answers).length

  return (
    <div className="page exam with-scratch">
      <div className="work-split">
        <div className="work-main">
          <div className="exam-header">
            <div>
              <strong>{exam.kind === 'mixed' ? 'Mixed exam' : `Focused exam · ${BANK_NAMES[exam.bank!]}`}</strong>
              <div className="muted">
                Question {idx + 1} of {questions.length} · {answeredCount} answered
              </div>
            </div>
            <Clock elapsedMs={elapsed} limitMin={exam.timeLimitMin} />
          </div>

          <div className="navigator">
            {questions.map((x, i) => {
              const cls = ['nav-dot']
              if (i === idx) cls.push('current')
              if (exam.answers[x.id]) cls.push('answered')
              if (exam.flagged.includes(x.id)) cls.push('flagged')
              return (
                <button key={x.id} className={cls.join(' ')} onClick={() => setCurrent(i)}>
                  {i + 1}
                </button>
              )
            })}
          </div>

          <div className="card">
            <QuestionView
              key={q.id}
              q={q}
              value={exam.answers[q.id] ?? ''}
              onChange={setAnswer}
              onSubmit={() => idx < questions.length - 1 && setCurrent(idx + 1)}
            />
            <div className="row spread">
              <button className="btn" onClick={() => setCurrent(idx - 1)} disabled={idx === 0}>
                ← Previous
              </button>
              <button className={exam.flagged.includes(q.id) ? 'btn flag on' : 'btn flag'} onClick={toggleFlag}>
                ⚑ {exam.flagged.includes(q.id) ? 'Flagged' : 'Flag for review'}
              </button>
              {idx < questions.length - 1 ? (
                <button className="btn primary" onClick={() => setCurrent(idx + 1)}>
                  Next →
                </button>
              ) : (
                <button className="btn primary" onClick={() => setConfirming(true)}>
                  Finish exam
                </button>
              )}
            </div>
          </div>

          <div className="row end">
            <button className="btn danger ghost" onClick={() => setConfirming(true)}>
              Submit exam now
            </button>
          </div>
        </div>
        <Scratchpad id={`exam-${exam.id}-${q.id}`} />
      </div>

      {confirming && (
        <div className="modal-backdrop" onClick={() => setConfirming(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Submit the exam?</h2>
            <p>
              You answered {answeredCount} of {questions.length} questions.
              {answeredCount < questions.length ? ' Unanswered questions count as wrong.' : ''}
            </p>
            <div className="row">
              <button className="btn primary" onClick={() => finish(false)}>
                Submit
              </button>
              <button className="btn" onClick={() => setConfirming(false)}>
                Keep working
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export function ExamReview({ exam }: { exam: ExamRecord }) {
  const { banks } = useApp()
  const [open, setOpen] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'wrong'>('all')
  const rows = exam.results.filter((r) => filter === 'all' || !r.correct)
  return (
    <div className="review">
      <div className="row">
        <button className={filter === 'all' ? 'tab active' : 'tab'} onClick={() => setFilter('all')}>
          All questions
        </button>
        <button className={filter === 'wrong' ? 'tab active' : 'tab'} onClick={() => setFilter('wrong')}>
          Wrong or skipped ({exam.results.filter((r) => !r.correct).length})
        </button>
      </div>
      {rows.map((r) => {
        const q = banks.byId.get(r.qid)
        const i = exam.results.indexOf(r)
        if (!q) return null
        const isOpen = open === r.qid
        return (
          <div key={r.qid} className={`review-item ${r.correct ? 'right' : 'wrong'}`}>
            <button className="review-head" onClick={() => setOpen(isOpen ? null : r.qid)}>
              <span className="review-num">{i + 1}</span>
              <span className="review-mark">{r.correct ? '✅' : r.answer ? '❌' : '⬜'}</span>
              <span className="review-text">{plainPreview(q.prompt)}</span>
              <span className="review-pts">
                {r.points}/{r.maxPoints}
              </span>
            </button>
            {isOpen && (
              <div className="review-body">
                <SourceTag q={q} />
                <Markdown text={q.prompt} />
                {q.image && <QuestionImage src={q.image} />}
                {q.type === 'mc' && q.choices && q.choices.some((c) => c.text) && (
                  <div className="choices static">
                    {q.choices.map((c) => (
                      <div
                        key={c.key}
                        className={`choice ${c.key === q.answer ? 'right' : ''} ${c.key === r.answer && !r.correct ? 'wrong' : ''}`}
                      >
                        <span className="choice-key">{c.key}</span>
                        <Markdown text={c.text} inline />
                      </div>
                    ))}
                  </div>
                )}
                <p>
                  Your answer: <strong>{r.answer || '(skipped)'}</strong> · Correct answer: <strong>{formatAnswer(q)}</strong>
                </p>
                <Solutions q={q} />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export function ExamResultPage({ id }: { id: string }) {
  const { data } = useApp()
  const exam = data.exams.find((e) => e.id === id)
  if (!exam) {
    return (
      <div className="page narrow">
        <div className="card">Exam not found.</div>
      </div>
    )
  }
  const pct = exam.maxScore ? Math.round((100 * exam.score) / exam.maxScore) : 0
  return (
    <div className="page">
      <h1 className="title">Exam results</h1>
      <div className="card result-summary">
        <div className="big-score">
          {exam.score}
          <span>/{exam.maxScore}</span>
        </div>
        <div>
          <div>
            <strong>{exam.correctCount}</strong> of {exam.results.length} correct · {pct}%
          </div>
          <div>
            Time: <strong>{formatDuration(exam.elapsedMs)}</strong>
            {exam.timeLimitMin ? ` of ${exam.timeLimitMin} min` : ''}
            {exam.timedOut ? ' · time ran out' : ''}
          </div>
          <div className="muted">
            {exam.kind === 'mixed' ? 'Mixed exam' : `Focused exam · ${BANK_NAMES[exam.bank!]}`} ·{' '}
            {new Date(exam.finishedAt).toLocaleString()}
          </div>
        </div>
        <div className="row">
          <button className="btn primary" onClick={() => navigate('/')}>
            Home
          </button>
        </div>
      </div>
      <ExamReview exam={exam} />
    </div>
  )
}
