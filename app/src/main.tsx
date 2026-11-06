import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AppProvider } from './state'
import { loadIndex } from './lib/banks'

const root = createRoot(document.getElementById('root')!)
root.render(<div className="loading">Loading questions…</div>)

loadIndex()
  .then((index) =>
    root.render(
      <StrictMode>
        <AppProvider index={index}>
          <App />
        </AppProvider>
      </StrictMode>,
    ),
  )
  .catch((e) => root.render(<div className="loading">Could not load the question banks: {String(e)}</div>))
