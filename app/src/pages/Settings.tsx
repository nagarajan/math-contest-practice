import { useState } from 'react'
import { useApp } from '../state'
import { navigate } from '../router'
import { gradeName, profileGrade, type ThemePref } from '../types'
import { ProfileForm } from './Profiles'

export function SettingsPage() {
  const { settings, setSettings, profile, profiles, clearHistory, removeProfile, updateProfile, resetApp, selectProfile, banks, grade, data } =
    useApp()
  const g = String(grade)
  const hasSelf = banks.all.some((q) => q.type === 'self')
  const [confirm, setConfirm] = useState<null | 'history' | 'profile' | 'all'>(null)
  const [editing, setEditing] = useState(false)
  const [limitText, setLimitText] = useState(settings.examTimeLimitMin ? String(settings.examTimeLimitMin) : '75')

  const setTheme = (theme: ThemePref) => setSettings({ ...settings, theme })

  const doConfirm = () => {
    if (confirm === 'history') clearHistory()
    if (confirm === 'profile' && profile) {
      removeProfile(profile.id)
      navigate('/profiles')
    }
    if (confirm === 'all') {
      resetApp()
      navigate('/profiles')
    }
    setConfirm(null)
  }

  return (
    <div className="page narrow">
      <h1 className="title">Settings</h1>

      <section className="card">
        <h2>Appearance</h2>
        <div className="segmented">
          {(['light', 'dark', 'system'] as ThemePref[]).map((t) => (
            <button key={t} className={settings.theme === t ? 'seg active' : 'seg'} onClick={() => setTheme(t)}>
              {t === 'light' ? '☀️ Light' : t === 'dark' ? '🌙 Dark' : '🖥 System'}
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>Exams</h2>
        <label className="check">
          <input
            type="checkbox"
            checked={settings.examTimeLimitMin !== null}
            onChange={(e) => setSettings({ ...settings, examTimeLimitMin: e.target.checked ? Math.max(1, Number(limitText) || 75) : null })}
          />
          Use a time limit
        </label>
        {settings.examTimeLimitMin !== null && (
          <label className="inline-field">
            Minutes:
            <input
              className="text-input small"
              type="number"
              min={1}
              max={300}
              value={limitText}
              onChange={(e) => {
                setLimitText(e.target.value)
                const n = Number(e.target.value)
                if (n >= 1) setSettings({ ...settings, examTimeLimitMin: Math.round(n) })
              }}
            />
            <span className="muted">(e.g. Math Kangaroo: 75 min for 30 questions; AMC 10/12: 75 min for 25)</span>
          </label>
        )}
        <label className="inline-field">
          Questions per mixed exam:
          <input
            className="text-input small"
            type="number"
            min={5}
            max={60}
            value={settings.examQuestionCount}
            onChange={(e) => {
              const n = Math.round(Number(e.target.value))
              if (n >= 5 && n <= 60) setSettings({ ...settings, examQuestionCount: n })
            }}
          />
        </label>
      </section>

      <section className="card">
        <h2>Practice</h2>
        <p className="muted">Which question banks general practice draws from ({gradeName(grade)}):</p>
        {banks.banks.map((b) => (
          <label key={b.id} className="check">
            <input
              type="checkbox"
              checked={!settings.practiceExcluded.includes(b.id)}
              onChange={(e) => {
                const excluded = e.target.checked ? settings.practiceExcluded.filter((x) => x !== b.id) : [...settings.practiceExcluded, b.id]
                if (banks.banks.some((x) => !excluded.includes(x.id))) setSettings({ ...settings, practiceExcluded: excluded })
              }}
            />
            {b.name} <span className="muted">({b.countsByGrade[g]} questions)</span>
          </label>
        ))}
        {hasSelf && (
          <label className="check">
            <input
              type="checkbox"
              checked={settings.practiceSelfGraded}
              onChange={(e) => setSettings({ ...settings, practiceSelfGraded: e.target.checked })}
            />
            Include proof problems (you check your own work against the solution)
          </label>
        )}
      </section>

      <section className="card">
        <h2>Profile</h2>
        {profile && !editing && (
          <div className="row">
            <span className="profile-avatar">{profile.avatar}</span>
            <strong>{profile.name}</strong>
            <span className="muted">{gradeName(profileGrade(profile))}</span>
            <button className="btn" onClick={() => setEditing(true)}>
              Edit
            </button>
            {profiles.length > 1 && (
              <button
                className="btn"
                onClick={() => {
                  selectProfile(null)
                  navigate('/profiles')
                }}
              >
                Switch profile
              </button>
            )}
          </div>
        )}
        {profile && editing && (
          <ProfileForm
            initialName={profile.name}
            initialAvatar={profile.avatar}
            initialGrade={profileGrade(profile)}
            submitLabel="Save"
            onSubmit={(n, a, gr) => {
              updateProfile(profile.id, { name: n, avatar: a, ...(data.examInProgress ? {} : { grade: gr }) })
              setEditing(false)
            }}
            onCancel={() => setEditing(false)}
          />
        )}
      </section>

      <section className="card danger-zone">
        <h2>Start fresh</h2>
        <div className="danger-row">
          <div>
            <strong>Erase {profile?.name}'s history</strong>
            <div className="muted">Deletes all practice answers, exams and progress for this profile. The profile stays.</div>
          </div>
          <button className="btn danger" onClick={() => setConfirm('history')}>
            Erase history
          </button>
        </div>
        <div className="danger-row">
          <div>
            <strong>Delete this profile</strong>
            <div className="muted">Removes {profile?.name} and all of their history.</div>
          </div>
          <button className="btn danger" onClick={() => setConfirm('profile')}>
            Delete profile
          </button>
        </div>
        <div className="danger-row">
          <div>
            <strong>Erase everything</strong>
            <div className="muted">Deletes every profile, all history and settings on this device.</div>
          </div>
          <button className="btn danger" onClick={() => setConfirm('all')}>
            Erase all data
          </button>
        </div>
      </section>

      {confirm && (
        <div className="modal-backdrop" onClick={() => setConfirm(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Are you sure?</h2>
            <p>
              {confirm === 'history' && `All of ${profile?.name}'s practice and exam history will be permanently erased.`}
              {confirm === 'profile' && `${profile?.name}'s profile and history will be permanently deleted.`}
              {confirm === 'all' && 'All profiles, history and settings will be permanently erased.'} This cannot be undone.
            </p>
            <div className="row">
              <button className="btn danger" onClick={doConfirm}>
                Yes, erase
              </button>
              <button className="btn" onClick={() => setConfirm(null)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
