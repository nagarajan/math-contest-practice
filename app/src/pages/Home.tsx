import { useApp } from '../state'
import { navigate } from '../router'
import { formatDuration } from '../components/Timer'
import { examTitle } from './Exam'
import { GradeSelect } from './Profiles'

export function HomePage() {
  const { profile, data, banks, settings, grade, updateProfile, index } = useApp()
  const g = String(grade)

  const inGrade = new Set(banks.all.map((q) => q.id))
  const practiced = data.attempts.filter((a) => a.mode === 'practice' && inGrade.has(a.qid))
  const correct = practiced.filter((a) => a.correct).length
  const seenIds = Object.keys(data.stats).filter((id) => inGrade.has(id)).length
  const toRevisit = Object.entries(data.stats).filter(([id, s]) => inGrade.has(id) && !s.lastCorrect).length
  const lastExam = data.exams[data.exams.length - 1]
  const examBanks = banks.banks.filter((b) => b.examCountsByGrade[g])

  return (
    <div className="page">
      <div className="home-head">
        <h1 className="title">
          Hi {profile?.name}! {profile?.avatar}
        </h1>
        <label className="grade-chip">
          <span className="muted">Practising at</span>
          <GradeSelect
            value={grade}
            counts={index.gradeCounts}
            disabled={!!data.examInProgress}
            onChange={(v) => profile && updateProfile(profile.id, { grade: v })}
          />
        </label>
      </div>

      {data.examInProgress && (
        <div className="card resume">
          <div>
            <strong>You have an exam in progress.</strong>
            <div className="muted">
              {examTitle(index, data.examInProgress)} · {Object.keys(data.examInProgress.answers).length}/{data.examInProgress.qids.length} answered
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
        <button className="mode-card mixed" onClick={() => navigate('/exam/new/mixed')} disabled={!!data.examInProgress || !examBanks.length}>
          <span className="mode-icon">🧩</span>
          <span className="mode-name">Mixed exam</span>
          <span className="mode-desc">
            {settings.examQuestionCount} questions split evenly across {examBanks.length > 1 ? `all ${examBanks.length} competitions` : 'the competitions'}, timed
            {settings.examTimeLimitMin ? ` (${settings.examTimeLimitMin} min limit)` : ''}.
          </span>
        </button>
        <button className="mode-card focused" onClick={() => navigate('/exam/new/focused')} disabled={!!data.examInProgress || !examBanks.length}>
          <span className="mode-icon">🏆</span>
          <span className="mode-name">Focused exam</span>
          <span className="mode-desc">A full paper from one competition of your choice, timed.</span>
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
        Question banks for this grade: {banks.banks.map((b) => `${b.name} ${b.countsByGrade[g]}`).join(' · ')}
      </div>
    </div>
  )
}
