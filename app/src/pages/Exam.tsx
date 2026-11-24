import { useEffect, useMemo, useRef, useState } from 'react'
import { useApp } from '../state'
import { navigate } from '../router'
import { gradeName, type Attempt, type BankId, type ExamKind, type ExamRecord, type Question } from '../types'
import { buildExam } from '../lib/selection'
import { formatAnswer, plainPreview, questionPoints, scoreAnswer } from '../lib/answers'
import { bankMeta, examTitle } from '../lib/banks'
import { useLookup } from '../lib/useLookup'
import { newId, recordExam } from '../lib/storage'
import { BankPill, QuestionView, SourceTag, QuestionImage } from '../components/QuestionView'
import { Solutions } from '../components/Solutions'
import { Clock, formatDuration, useNow } from '../components/Timer'
import { Markdown } from '../components/Markdown'
import { Scratchpad, discardScratch } from '../components/Scratchpad'
import { GradeChip } from './Profiles'

export function ExamSetupPage({ kind }: { kind: ExamKind }) {
  const { banks, data, updateData, settings, grade } = useApp()
  const g = String(grade)
  const examBanks = banks.banks.filter((b) => (b.examCountsByGrade[g] ?? 0) > 0)
  const practiceOnly = banks.banks.filter((b) => !(b.examCountsByGrade[g] ?? 0))
  const [bank, setBank] = useState<BankId | null>(examBanks[0]?.id ?? null)
  const bankAll = examBanks.find((b) => b.id === bank)
  const meta = bankAll && { ...bankAll, ...bankAll.byGrade?.[g] }

  const available = kind === 'mixed' ? examBanks.reduce((a, b) => a + b.examCountsByGrade[g], 0) : (meta?.examCountsByGrade[g] ?? 0)
  const wanted = kind === 'focused' && meta?.examLength ? meta.examLength : settings.examQuestionCount
  const n = Math.min(wanted, available)

  const start = () => {
    const qs = buildExam(banks.all, data, kind === 'focused' ? bank : null, wanted)
    const now = Date.now()
    updateData((d) => ({
      ...d,
      examInProgress: {
        id: newId(),
        kind,
        bank: kind === 'focused' ? bank : null,
        grade,
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

  const notes = kind === 'mixed' ? examBanks : meta ? [meta] : []

  return (
    <div className="page narrow">
      <div className="home-head">
        <h1 className="title">{kind === 'mixed' ? 'Mixed exam' : 'Focused exam'}</h1>
        <GradeChip label="Grade" />
      </div>
      <div className="card">
        {kind === 'focused' && (
          <>
            <h2>Choose a competition</h2>
            <div className="bank-choices">
              {examBanks.map((b) => (
                <button key={b.id} className={b.id === bank ? 'bank-choice selected' : 'bank-choice'} onClick={() => setBank(b.id)}>
                  <BankPill bank={b.id} />
                  <span className="muted">{b.examCountsByGrade[g]} questions</span>
                </button>
              ))}
            </div>
          </>
        )}
        {!examBanks.length ? (
          <p>
            There are no exam-style (auto-checked) questions for {gradeName(grade)} yet. The problems at this level are proofs, which
            you can work through in General practice.
          </p>
        ) : (
          <ul className="exam-facts">
            <li>
              <strong>{n} questions</strong>
              {kind === 'focused' && meta?.examLength ? ' (the length of a real paper)' : ''}
              {n < wanted ? ` (only ${available} available)` : ''}, ordered from easier to harder, for {gradeName(grade)}.
            </li>
            <li>
              {settings.examTimeLimitMin
                ? `Time limit: ${settings.examTimeLimitMin} minutes. The exam is submitted automatically when time runs out.`
                : 'No time limit — the clock shows how long you take.'}
              {kind === 'focused' && meta?.examMinutes ? ` The real contest allows ${meta.examMinutes} minutes.` : ''}
            </li>
            <li>You can move between questions and change answers until you submit.</li>
            {notes.map((b) => (
              <li key={b.id}>
                <strong>{b.name}:</strong> {b.scoringNote}
              </li>
            ))}
            {kind === 'mixed' && practiceOnly.length > 0 && (
              <li className="muted">Proof problems ({practiceOnly.map((b) => b.name).join(', ')}) are practice-only.</li>
            )}
          </ul>
        )}
        <button className="btn primary big" onClick={start} disabled={!n}>
          Start exam
        </button>
      </div>
    </div>
  )
}

export function ExamRunPage() {
  const { data, updateData, index } = useApp()
  const exam = data.examInProgress
  const lookup = useLookup([exam?.grade], exam?.qids ?? [])
  const now = useNow(500)
  const [confirming, setConfirming] = useState(false)
  const finishing = useRef(false)

  const questions = useMemo(
    () => (exam ? exam.qids.map((id) => lookup.get(id)).filter((q): q is Question => !!q) : []),
    [exam, lookup],
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
      const { correct, points } = scoreAnswer(q, answer, bankMeta(index, q.bank))
      return { qid: q.id, answer, correct, points, maxPoints: questionPoints(q) }
    })
    const record: ExamRecord = {
      id: exam.id,
      kind: exam.kind,
      bank: exam.bank,
      grade: exam.grade,
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
      bank: lookup.get(r.qid)!.bank,
      answer: r.answer,
      correct: r.correct,
      at: finishedAt,
      ms: 0,
      mode: 'exam',
      examId: exam.id,
      grade: exam.grade,
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
  if (!questions.length) return <div className="loading">Loading exam…</div>

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
              <strong>{examTitle(index, exam)}</strong>
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
  const lookup = useLookup([exam.grade], exam.results.map((r) => r.qid))
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
        const q = lookup.get(r.qid)
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
                  Your answer: <strong>{r.answer || '(skipped)'}</strong> · Correct answer:{' '}
                  <strong>
                    <Markdown text={formatAnswer(q)} inline />
                  </strong>
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
  const { data, index } = useApp()
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
            {examTitle(index, exam)} · {gradeName(exam.grade ?? 5)} · {new Date(exam.finishedAt).toLocaleString()}
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
