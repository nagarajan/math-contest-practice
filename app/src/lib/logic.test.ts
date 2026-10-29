import { describe, expect, it } from 'vitest'
import { isCorrect, parseNumber } from './answers'
import { buildExam, pickPracticeQuestion, questionWeight, RETRY_AFTER_MS, WEIGHT_CORRECT, WEIGHT_UNSEEN, WEIGHT_WRONG } from './selection'
import { emptyData, recordAttempt } from './storage'
import type { Question } from '../types'

const q = (over: Partial<Question>): Question => ({
  id: 'x',
  bank: 'moems',
  source: { contest: 'c', paper: 'p', year: 2020, number: 1, url: '' },
  grade: '5',
  points: null,
  timeMinutes: null,
  type: 'numeric',
  prompt: 'p',
  image: null,
  choices: null,
  answer: '42',
  acceptedAnswers: null,
  answerUnit: null,
  solutions: [],
  topics: ['arithmetic'],
  difficulty: 1,
  ...over,
})

describe('parseNumber', () => {
  it.each([
    ['42', 42],
    [' 42 cm', 42],
    ['$4.25', 4.25],
    ['3/4', 0.75],
    ['2 1/2', 2.5],
    ['1,000', 1000],
    ['.5', 0.5],
    ['64 apples', 64],
    ['12 sq cm', 12],
    ['-6', -6],
  ])('%s -> %s', (s, v) => expect(parseNumber(s)).toBeCloseTo(v))
  it.each(['', 'abc', '1/0', '12 3'])('%s is not a number', (s) => expect(parseNumber(s)).toBeNull())
})

describe('isCorrect', () => {
  it('numeric forms are equivalent', () => {
    const n = q({ answer: '1/2' })
    expect(isCorrect(n, '0.5')).toBe(true)
    expect(isCorrect(n, '2/4')).toBe(true)
    expect(isCorrect(n, '0.6')).toBe(false)
  })
  it('text answers use accepted forms, case-insensitively', () => {
    const t = q({ type: 'text', answer: 'Wednesday', acceptedAnswers: ['Wed'] })
    expect(isCorrect(t, ' wednesday ')).toBe(true)
    expect(isCorrect(t, 'WED')).toBe(true)
    expect(isCorrect(t, 'Thursday')).toBe(false)
  })
  it('multiple choice compares keys', () => {
    const m = q({ type: 'mc', answer: 'C', choices: [{ key: 'A', text: '1' }, { key: 'C', text: '3' }] })
    expect(isCorrect(m, 'c')).toBe(true)
    expect(isCorrect(m, 'A')).toBe(false)
    expect(isCorrect({ ...m, acceptedAnswers: ['A'] }, 'A')).toBe(true)
  })
})

describe('practice scheduler', () => {
  const now = 10 * RETRY_AFTER_MS
  it('orders weights wrong > unseen > correct', () => {
    expect(WEIGHT_WRONG).toBeGreaterThan(WEIGHT_UNSEEN)
    expect(WEIGHT_UNSEEN).toBeGreaterThan(WEIGHT_CORRECT)
  })
  it('a wrong question is blocked until 10 more questions or 1 hour', () => {
    let d = recordAttempt(emptyData(), { qid: 'w', bank: 'moems', answer: '1', correct: false, at: now, ms: 0, mode: 'practice' })
    expect(questionWeight(d.stats.w, d.seq, now + 1000)).toBe(0)
    for (let i = 0; i < 9; i++) d = recordAttempt(d, { qid: `o${i}`, bank: 'moems', answer: '1', correct: true, at: now, ms: 0, mode: 'practice' })
    expect(questionWeight(d.stats.w, d.seq, now + 1000)).toBe(0)
    d = recordAttempt(d, { qid: 'o9', bank: 'moems', answer: '1', correct: true, at: now, ms: 0, mode: 'practice' })
    expect(questionWeight(d.stats.w, d.seq, now + 1000)).toBe(WEIGHT_WRONG)
    const d2 = recordAttempt(emptyData(), { qid: 'w', bank: 'moems', answer: '1', correct: false, at: now, ms: 0, mode: 'practice' })
    expect(questionWeight(d2.stats.w, d2.seq, now + RETRY_AFTER_MS)).toBe(WEIGHT_WRONG)
  })
  it('correct answers decay further with a streak', () => {
    let d = emptyData()
    d = recordAttempt(d, { qid: 'c', bank: 'moems', answer: '1', correct: true, at: 0, ms: 0, mode: 'practice' })
    const w1 = questionWeight(d.stats.c, d.seq, now)
    d = recordAttempt(d, { qid: 'c', bank: 'moems', answer: '1', correct: true, at: 0, ms: 0, mode: 'practice' })
    expect(questionWeight(d.stats.c, d.seq, now)).toBeLessThan(w1)
  })
  it('never returns the question just shown when others exist', () => {
    const pool = [q({ id: 'a' }), q({ id: 'b' })]
    for (let i = 0; i < 50; i++) expect(pickPracticeQuestion(pool, emptyData(), ['moems'], 'a')?.id).toBe('b')
  })
  it('falls back to the oldest question when everything is cooling down', () => {
    let d = emptyData()
    d = recordAttempt(d, { qid: 'a', bank: 'moems', answer: '', correct: false, at: now, ms: 0, mode: 'practice' })
    d = recordAttempt(d, { qid: 'b', bank: 'moems', answer: '', correct: false, at: now, ms: 0, mode: 'practice' })
    d = recordAttempt(d, { qid: 'c', bank: 'moems', answer: '', correct: false, at: now, ms: 0, mode: 'practice' })
    const pool = [q({ id: 'a' }), q({ id: 'b' }), q({ id: 'c' })]
    expect(pickPracticeQuestion(pool, d, ['moems'], 'c', now)?.id).toBe('a')
  })
})

describe('buildExam', () => {
  const pool = Array.from({ length: 90 }, (_, i) =>
    q({ id: `k${i}`, bank: 'kangaroo', type: 'mc', points: [3, 4, 5][i % 3], difficulty: ([1, 2, 3] as const)[i % 3] }),
  ).concat(Array.from({ length: 40 }, (_, i) => q({ id: `m${i}` })))
  it('builds 30 distinct questions ordered by difficulty', () => {
    const e = buildExam(pool, emptyData(), null, 30)
    expect(new Set(e.map((x) => x.id)).size).toBe(30)
    for (let i = 1; i < e.length; i++) expect(e[i].difficulty).toBeGreaterThanOrEqual(e[i - 1].difficulty - 0)
  })
  it('focused Kangaroo exam has 10 questions of each point value', () => {
    const e = buildExam(pool, emptyData(), 'kangaroo', 30)
    expect(e.every((x) => x.bank === 'kangaroo')).toBe(true)
    expect(e.filter((x) => x.points === 3).length).toBe(10)
    expect(e.filter((x) => x.points === 5).length).toBe(10)
  })
  it('uses what exists when a bank is small', () => {
    expect(buildExam(pool, emptyData(), 'noetic', 30)).toHaveLength(0)
    expect(buildExam(pool, emptyData(), 'moems', 30)).toHaveLength(30)
  })
  it('mixed exams split evenly across banks and fill shortfalls from the rest', () => {
    const three = pool.concat(Array.from({ length: 6 }, (_, i) => q({ id: `n${i}`, bank: 'noetic' })))
    const e = buildExam(three, emptyData(), null, 30)
    expect(e).toHaveLength(30)
    expect(e.filter((x) => x.bank === 'noetic')).toHaveLength(6)
    expect(e.filter((x) => x.bank === 'kangaroo').length).toBeGreaterThanOrEqual(10)
    expect(e.filter((x) => x.bank === 'moems').length).toBeGreaterThanOrEqual(10)
  })
})
