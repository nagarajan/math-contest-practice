import { useState } from 'react'
import { useApp } from '../state'
import { navigate } from '../router'

export const AVATARS = ['🦘', '🦉', '🐼', '🦊', '🐯', '🐙', '🦄', '🐢', '🚀', '⭐', '🧠', '🎯']

export function ProfileForm({
  initialName = '',
  initialAvatar = AVATARS[0],
  submitLabel,
  onSubmit,
  onCancel,
}: {
  initialName?: string
  initialAvatar?: string
  submitLabel: string
  onSubmit: (name: string, avatar: string) => void
  onCancel?: () => void
}) {
  const [name, setName] = useState(initialName)
  const [avatar, setAvatar] = useState(initialAvatar)
  return (
    <form
      className="profile-form"
      onSubmit={(e) => {
        e.preventDefault()
        if (name.trim()) onSubmit(name, avatar)
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
          </button>
        ))}
        {!adding && (
          <button className="profile-card add" onClick={() => setAdding(true)}>
            <span className="profile-avatar">＋</span>
            <span>Add a kid</span>
          </button>
        )}
      </div>
      {adding && (
        <div className="card">
          <h2>New profile</h2>
          <ProfileForm
            submitLabel="Create"
            onSubmit={(name, avatar) => {
              const p = addProfile(name, avatar)
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
