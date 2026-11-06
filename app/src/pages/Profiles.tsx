import { useState } from 'react'
import { useApp } from '../state'
import { navigate } from '../router'
import { DEFAULT_GRADE, GRADES, gradeName, profileGrade, type Grade } from '../types'

export const AVATARS = ['🦘', '🦉', '🐼', '🦊', '🐯', '🐙', '🦄', '🐢', '🚀', '⭐', '🧠', '🎯']

export function GradeSelect({
  value,
  onChange,
  counts,
  disabled,
}: {
  value: Grade
  onChange: (g: Grade) => void
  counts: Record<string, number>
  disabled?: boolean
}) {
  return (
    <select
      className="grade-select"
      value={value}
      disabled={disabled}
      title={disabled ? 'Finish the exam in progress before changing grade' : 'Grade level'}
      onChange={(e) => onChange(Number(e.target.value))}
    >
      {GRADES.map((g) => (
        <option key={g} value={g} disabled={!counts[String(g)]}>
          {gradeName(g)}
          {counts[String(g)] ? ` (${counts[String(g)]} questions)` : ' (no questions yet)'}
        </option>
      ))}
    </select>
  )
}

export function ProfileForm({
  initialName = '',
  initialAvatar = AVATARS[0],
  initialGrade = DEFAULT_GRADE,
  submitLabel,
  onSubmit,
  onCancel,
}: {
  initialName?: string
  initialAvatar?: string
  initialGrade?: Grade
  submitLabel: string
  onSubmit: (name: string, avatar: string, grade: Grade) => void
  onCancel?: () => void
}) {
  const { index } = useApp()
  const [name, setName] = useState(initialName)
  const [avatar, setAvatar] = useState(initialAvatar)
  const [grade, setGrade] = useState<Grade>(initialGrade)
  return (
    <form
      className="profile-form"
      onSubmit={(e) => {
        e.preventDefault()
        if (name.trim()) onSubmit(name, avatar, grade)
      }}
    >
      <input className="text-input" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} autoFocus />
      <div className="avatar-grid">
        {AVATARS.map((a) => (
          <button type="button" key={a} className={a === avatar ? 'avatar selected' : 'avatar'} onClick={() => setAvatar(a)}>
            {a}
          </button>
        ))}
      </div>
      <label className="inline-field">
        Grade: <GradeSelect value={grade} onChange={setGrade} counts={index.gradeCounts} />
      </label>
      <div className="row">
        <button className="btn primary" type="submit" disabled={!name.trim()}>
          {submitLabel}
        </button>
        {onCancel && (
          <button className="btn" type="button" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}

export function ProfilesPage() {
  const { profiles, selectProfile, addProfile } = useApp()
  const [adding, setAdding] = useState(profiles.length === 0)
  return (
    <div className="page narrow">
      <h1 className="title">Who is practicing?</h1>
      <div className="profile-list">
        {profiles.map((p) => (
          <button
            key={p.id}
            className="profile-card"
            onClick={() => {
              selectProfile(p.id)
              navigate('/')
            }}
          >
            <span className="profile-avatar">{p.avatar}</span>
            <span>{p.name}</span>
            <span className="muted small">{gradeName(profileGrade(p), true)}</span>
          </button>
        ))}
        {!adding && (
          <button className="profile-card add" onClick={() => setAdding(true)}>
            <span className="profile-avatar">＋</span>
            <span>Add a profile</span>
          </button>
        )}
      </div>
      {adding && (
        <div className="card">
          <h2>New profile</h2>
          <ProfileForm
            submitLabel="Create"
            onSubmit={(name, avatar, grade) => {
              const p = addProfile(name, avatar, grade)
              selectProfile(p.id)
              navigate('/')
            }}
            onCancel={profiles.length ? () => setAdding(false) : undefined}
          />
        </div>
      )}
    </div>
  )
}
