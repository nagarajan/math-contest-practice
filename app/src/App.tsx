import { useEffect } from 'react'
import { useApp } from './state'
import { navigate, useRoute } from './router'
import { HomePage } from './pages/Home'
import { PracticePage } from './pages/Practice'
import { ExamResultPage, ExamRunPage, ExamSetupPage } from './pages/Exam'
import { HistoryPage } from './pages/History'
import { SettingsPage } from './pages/Settings'
import { ProfilesPage } from './pages/Profiles'
import { SourcesPage } from './pages/Sources'

function useTheme() {
  const { settings } = useApp()
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const apply = () => {
      const dark = settings.theme === 'dark' || (settings.theme === 'system' && mq.matches)
      document.documentElement.dataset.theme = dark ? 'dark' : 'light'
    }
    apply()
    mq.addEventListener('change', apply)
    return () => mq.removeEventListener('change', apply)
  }, [settings.theme])
}

export default function App() {
  useTheme()
  const { profile, settings, setSettings } = useApp()
  const route = useRoute()
  const [page, a] = route

  const inExam = page === 'exam' && a === 'run'

  let body
  if (!profile || page === 'profiles') body = <ProfilesPage />
  else if (page === 'practice') body = <PracticePage />
  else if (page === 'exam' && a === 'new') body = <ExamSetupPage key={route[2]} kind={route[2] === 'focused' ? 'focused' : 'mixed'} />
  else if (inExam) body = <ExamRunPage />
  else if (page === 'exam' && a === 'result') body = <ExamResultPage id={route[2]} />
  else if (page === 'history') body = <HistoryPage />
  else if (page === 'settings') body = <SettingsPage />
  else if (page === 'sources') body = <SourcesPage />
  else body = <HomePage />

  const isDark = settings.theme === 'dark' || (settings.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)

  return (
    <>
      <header className="topbar">
        <button className="brand" onClick={() => navigate('/')}>
          🦘 <span>Math Contest Practice</span>
        </button>
        {profile && !inExam && (
          <nav className="nav">
            <button className={!page ? 'nav-link active' : 'nav-link'} onClick={() => navigate('/')}>
              Home
            </button>
            <button className={page === 'practice' ? 'nav-link active' : 'nav-link'} onClick={() => navigate('/practice')}>
              Practice
            </button>
            <button className={page === 'history' ? 'nav-link active' : 'nav-link'} onClick={() => navigate('/history')}>
              History
            </button>
            <button className={page === 'settings' ? 'nav-link active' : 'nav-link'} onClick={() => navigate('/settings')} aria-label="Settings">
              ⚙️
            </button>
          </nav>
        )}
        <div className="topbar-right">
          <button
            className="icon-btn"
            title="Toggle light/dark theme"
            onClick={() => setSettings({ ...settings, theme: isDark ? 'light' : 'dark' })}
          >
            {isDark ? '☀️' : '🌙'}
          </button>
          {profile && !inExam && (
            <button className="profile-chip" onClick={() => navigate('/profiles')} title="Switch profile">
              {profile.avatar} {profile.name}
            </button>
          )}
        </div>
      </header>
      <main>{body}</main>
      {!inExam && (
        <footer className="footer muted">
          Questions © their respective competitions, used here for private practice only ·{' '}
          <button className="link" onClick={() => navigate('/sources')}>
            Question sources
          </button>
        </footer>
      )}
    </>
  )
}
