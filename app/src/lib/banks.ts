import { BANK_IDS, type BankId, type Question } from '../types'

export interface BankIndexEntry {
  id: BankId
  count: number
  sources: { contest: string; paper: string; year: number | null; count: number; url: string }[]
}

export interface LoadedBanks {
  all: Question[]
  byId: Map<string, Question>
  index: BankIndexEntry[]
}

export const assetUrl = (p: string) => `${import.meta.env.BASE_URL}${p.replace(/^\//, '')}`

export async function loadBanks(): Promise<LoadedBanks> {
  const index: BankIndexEntry[] = await fetch(assetUrl('banks/index.json')).then((r) => r.json())
  const lists = await Promise.all(
    BANK_IDS.map((b) =>
      fetch(assetUrl(`banks/${b}.json`))
        .then((r) => (r.ok ? r.json() : []))
        .catch(() => []),
    ),
  )
  const all = (lists as Question[][]).flat()
  return { all, byId: new Map(all.map((q) => [q.id, q])), index }
}
