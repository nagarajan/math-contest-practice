import { useEffect, useState } from 'react'
import { useApp } from '../state'
import type { Grade, Question } from '../types'
import { loadLookup, withContent } from './banks'

/** Records saved before grade levels existed came from the original grade 4-6 banks. */
const LEGACY_GRADES: Grade[] = [4, 5, 6]

/**
 * Questions by id across the given grades (history recorded at other grades). The questions in
 * `show` come with their text and answers; the map is empty until those have loaded.
 */
export function useLookup(grades: (Grade | undefined)[], show: string[]): Map<string, Question> {
  const { banks, index } = useApp()
  const wanted = [...new Set(grades.flatMap((g) => (g === undefined ? LEGACY_GRADES : [g])))].filter((g) => g !== banks.grade).sort()
  const key = wanted.join(',')
  const showKey = show.join(',')
  const [map, setMap] = useState<Map<string, Question>>(new Map())
  useEffect(() => {
    let live = true
    ;(async () => {
      const m = wanted.length ? await loadLookup(index, wanted) : new Map<string, Question>()
      for (const [id, q] of banks.byId) m.set(id, q)
      const full = await withContent(show.map((id) => m.get(id)).filter((q): q is Question => !!q))
      for (const q of full) m.set(q.id, q)
      if (live) setMap(m)
    })().catch(() => {})
    return () => {
      live = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, showKey, banks, index])
  return map
}
