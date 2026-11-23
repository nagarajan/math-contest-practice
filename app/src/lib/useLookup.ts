import { useEffect, useState } from 'react'
import { useApp } from '../state'
import type { Grade, Question } from '../types'
import { loadLookup } from './banks'

/** Records saved before grade levels existed came from the original grade 4-6 banks. */
const LEGACY_GRADES: Grade[] = [4, 5, 6]

/**
 * Questions by id across the given grades (history recorded at other grades), starting with
 * the current grade's questions while the others load.
 */
export function useLookup(grades: (Grade | undefined)[]): Map<string, Question> {
  const { banks, index } = useApp()
  const wanted = [...new Set(grades.flatMap((g) => (g === undefined ? LEGACY_GRADES : [g])))].filter((g) => g !== banks.grade).sort()
  const key = wanted.join(',')
  const [map, setMap] = useState<Map<string, Question>>(banks.byId)
  useEffect(() => {
    if (!wanted.length) {
      setMap(banks.byId)
      return
    }
    let live = true
    loadLookup(index, wanted).then((m) => {
      if (!live) return
      for (const [id, q] of banks.byId) m.set(id, q)
      setMap(m)
    })
    return () => {
      live = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, banks, index])
  return map
}
