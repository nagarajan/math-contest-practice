import { useEffect, useState } from 'react'

export function navigate(path: string) {
  window.location.hash = path
}

export function useRoute(): string[] {
  const parse = () => window.location.hash.replace(/^#\/?/, '').split('/').filter(Boolean)
  const [parts, setParts] = useState(parse)
  useEffect(() => {
    const on = () => {
      setParts(parse())
      window.scrollTo(0, 0)
    }
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return parts
}
