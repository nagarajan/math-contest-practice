import { useMemo } from 'react'
import { useApp } from '../state'
import { navigate } from '../router'
import { BANK_IDS, BANK_NAMES } from '../types'
import { formatDuration } from '../components/Timer'

export function HomePage() {
  const { profile, data, banks, settings } = useApp()

  const counts = useMemo(() => {
    const c = { kangaroo: 0, noetic: 0, moems: 0 }
    for (const q of banks.all) c[q.bank]++
    return c
  }, [banks])

  const practiced = data.attempts.filter((a) => a.mode === 'practice')
  const correct = practiced.filter((a) => a.correct).length
  const seenIds = Object.keys(data.stats).length
  const toRevisit = Object.values(data.stats).filter((s) => !s.lastCorrect).length
  const lastExam = data.exams[data.exams.length - 1]

  return (
    <div className="page">
      <h1 className="title">Hi {profile?.name}! {profile?.avatar}</h1>

      {data.examInProgress && (
        <div className="card resume">
          <div>
            <strong>You have an exam in progress.</strong>
            <div className="muted">
              {data.examInProgress.kind === 'mixed' ? 'Mixed exam' : `Focused exam: ${BANK_NAMES[data.examInProgress.bank!]}`} ·{' '}
              {Object.keys(data.examInProgress.answers).length}/{data.examInProgress.qids.length} answered
            </div>
          </div>
          <button className="btn primary" onClick={() => navigate('/exam/run')}>
            Resume exam
          </button>
        </div>
      )}

      <div className="mode-grid">
        <button className="mode-card practice" onClick={() => navigate('/practice')}>
          <span className="mode-icon">🎯</span>
          <span className="mode-name">General practice</span>
          <span className="mode-desc">One question at a time from all banks, with solutions. Missed questions come back later.</span>
        </button>
        <button className="mode-card mixed" onClick={() => navigate('/exam/new/mixed')} disabled={!!data.examInProgress}>
          <span className="mode-icon">🧩</span>
          <span className="mode-name">Mixed exam</span>
          <span className="mode-desc">
            {settings.examQuestionCount} questions split evenly across all three banks, timed
            {settings.examTimeLimitMin ? ` (${settings.examTimeLimitMin} min limit)` : ''}.
          </span>
        </button>
        <button className="mode-card focused" onClick={() => navigate('/exam/new/focused')} disabled={!!data.examInProgress}>
          <span className="mode-icon">🏆</span>
          <span className="mode-name">Focused exam</span>
          <span className="mode-desc">{settings.examQuestionCount} questions from one competition of your choice, timed.</span>
        </button>
      </div>

      <div className="stat-grid">
        <div className="stat">
          <div className="stat-value">{practiced.length}</div>
          <div className="stat-label">practice questions answered</div>
        </div>
        <div className="stat">
          <div className="stat-value">{practiced.length ? Math.round((100 * correct) / practiced.length) : 0}%</div>
          <div className="stat-label">practice accuracy</div>
        </div>
        <div className="stat">
          <div className="stat-value">
            {seenIds}/{banks.all.length}
          </div>
          <div className="stat-label">questions seen</div>
        </div>
        <div className="stat">
          <div className="stat-value">{toRevisit}</div>
          <div className="stat-label">to revisit</div>
        </div>
        <div className="stat">
          <div className="stat-value">{data.exams.length}</div>
          <div className="stat-label">exams taken</div>
        </div>
        {lastExam && (
          <div className="stat">
            <div className="stat-value">
              {lastExam.score}/{lastExam.maxScore}
            </div>
            <div className="stat-label">last exam · {formatDuration(lastExam.elapsedMs)}</div>
          </div>
        )}
      </div>

      <div className="bank-summary muted">
        Question banks:{' '}
        {BANK_IDS.map((b) => `${BANK_NAMES[b]} ${counts[b]}`).join(' · ')}
      </div>
    </div>
  )
}
