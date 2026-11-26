const analysisTimeMs = 2500
const dayMs = 24 * 60 * 60 * 1000

// Sample knee angles and repetition times taken from the handoff CSVs.
const sampleReps = [
  [[36.27, 1.60], [35.14, 1.68], [36.66, 1.64], [37.10, 1.72], [36.77, 1.68], [36.39, 1.68], [36.73, 1.68], [38.21, 1.72]],
  [[61.58, 0.88], [61.67, 1.08]],
  [[96.59, 1.30], [92.70, 1.37], [93.60, 1.23]],
]

function demoError(status, code, message) {
  return Object.assign(new Error(message), { status, code })
}

function checkSignal(signal) {
  signal?.throwIfAborted()
}

function makeSet(sessionId, setNumber, { target_reps, rpe, time, complete }) {
  const repData = sampleReps[(setNumber - 1) % sampleReps.length]
  const reps = repData.map(([angle, duration], index) => ({
    rep_index: index + 1,
    min_knee_angle: angle,
    duration_sec: duration,
  }))

  return {
    submittedAt: time - (complete ? analysisTimeMs : 0),
    result: {
      set_id: `${sessionId}-set-${setNumber}`,
      set_number: setNumber,
      status: 'completed',
      rep_count: reps.length,
      target_reps,
      rpe,
      recommended_rest_seconds: 60 + rpe * 10,
      next_target_reps: target_reps,
      change_score: Number((0.08 + setNumber * 0.03 + rpe / 50).toFixed(2)),
      reps,
      feedback: [{
        title: '동작 속도 유지하기',
        message: '다음 세트에서도 내려가고 올라오는 속도를 일정하게 유지해 보세요.',
      }],
    },
  }
}

function makeSession(id, startedAt, endedAt = null) {
  return { id, startedAt, endedAt, sets: [] }
}

function setState(entry, now) {
  const elapsed = now - entry.submittedAt
  if (elapsed >= analysisTimeMs) return { status: 'completed', stage: 3 }
  if (elapsed < 300) return { status: 'queued', stage: 0 }
  return { status: 'processing', stage: Math.min(3, Math.floor(elapsed / 660) + 1) }
}

function publicSet(entry, now) {
  const { status } = setState(entry, now)
  if (status !== 'completed') {
    const { set_id, set_number, target_reps, rpe } = entry.result
    return { set_id, set_number, target_reps, rpe, status }
  }

  return {
    ...entry.result,
    reps: entry.result.reps.map((rep) => ({ ...rep })),
    feedback: entry.result.feedback.map((item) => ({ ...item })),
  }
}

function publicSession(session, now) {
  const sets = session.sets.map((entry) => publicSet(entry, now))
  const completed = sets.filter((set) => set.status === 'completed')
  return {
    session_id: session.id,
    started_at: new Date(session.startedAt).toISOString(),
    ended_at: session.endedAt === null ? null : new Date(session.endedAt).toISOString(),
    status: session.endedAt === null ? 'in_progress' : 'completed',
    set_count: completed.length,
    total_reps: completed.reduce((sum, set) => sum + set.rep_count, 0),
    duration_seconds: Math.max(0, Math.floor(((session.endedAt ?? now) - session.startedAt) / 1000)),
    sets,
  }
}

function buildBaseline(entry) {
  const { set_id, reps } = entry.result
  const meanDuration = reps.reduce((sum, rep) => sum + rep.duration_sec, 0) / reps.length
  return {
    set_id,
    min_knee_angle: Math.min(...reps.map((rep) => rep.min_knee_angle)),
    torso_angle: 34,
    duration_sec: Number(meanDuration.toFixed(2)),
    created_at: new Date().toISOString(),
  }
}

export function createDemoApi() {
  const profile = { nickname: '폼핏 러너', email: 'demo@formfit.local' }
  const runs = [2, 4, 6].map((daysAgo, index) => {
    const startedAt = Date.now() - daysAgo * dayMs
    const endedAt = startedAt + (18 + index * 3) * 60 * 1000
    const session = makeSession(`sample-${index + 1}`, startedAt, endedAt)
    const count = index === 1 ? 3 : 2
    for (let i = 0; i < count; i++) {
      const entry = makeSet(session.id, i + 1, {
        target_reps: 10, rpe: 3 + (index % 2), time: endedAt, complete: true,
      })
      entry.result.change_score = Number((0.28 - index / 25 + i / 50).toFixed(2))
      session.sets.push(entry)
    }
    return session
  })
  let nextSessionId = 1
  let personalBaseline = null

  function getSession(id) {
    const session = runs.find((item) => item.id === String(id))
    if (!session) throw demoError(404, 'SESSION_NOT_FOUND', '운동을 찾을 수 없어요.')
    return session
  }

  function getSet(id) {
    const entry = runs.flatMap((session) => session.sets).find((item) => item.result.set_id === String(id))
    if (!entry) throw demoError(404, 'SET_NOT_FOUND', '세트를 찾을 수 없어요.')
    return entry
  }

  function activeSession() {
    return runs.find((item) => item.endedAt === null)
  }

  function completedSessions() {
    return runs.filter((item) => item.endedAt !== null)
  }

  return {
    async currentSession(signal) {
      checkSignal(signal)
      const current = activeSession()
      return current ? publicSession(current, Date.now()) : null
    },

    async baseline(signal) {
      checkSignal(signal)
      return personalBaseline ? { ...personalBaseline } : null
    },

    async sessions({ size = 20, page = 1, signal } = {}) {
      checkSignal(signal)
      const workouts = completedSessions()
      const start = (page - 1) * size
      const now = Date.now()
      const items = workouts.slice(start, start + size).map((session) => publicSession(session, now))
      return { items, total: workouts.length }
    },

    async createSession() {
      if (activeSession()) throw demoError(409, 'SESSION_IN_PROGRESS', '이미 진행 중인 운동이 있어요.')
      const now = Date.now()
      const session = makeSession(`demo-${nextSessionId++}`, now)
      runs.unshift(session)
      return publicSession(session, now)
    },

    async session(id, signal) {
      checkSignal(signal)
      return publicSession(getSession(id), Date.now())
    },

    async uploadSet(sessionId, { video, rpe, target_reps, use_sample = false }, signal) {
      checkSignal(signal)
      const session = getSession(sessionId)

      if (session.endedAt !== null) throw demoError(409, 'SESSION_ENDED', '이미 종료된 운동이에요.')
      if (!video && !use_sample) throw demoError(400, 'VIDEO_REQUIRED', '영상 파일을 선택해 주세요.')
      if (!Number.isInteger(rpe) || rpe < 1 || rpe > 5) {
        throw demoError(400, 'INVALID_RPE', '체감 피로도는 1~5 사이에서 선택해 주세요.')
      }

      const time = Date.now()
      if (session.sets.some((set) => setState(set, time).status !== 'completed')) {
        throw demoError(409, 'SET_PROCESSING', '앞선 세트의 분석이 진행 중이에요.')
      }

      const entry = makeSet(session.id, session.sets.length + 1, { target_reps, rpe, time, complete: false })
      session.sets.push(entry)
      return { set_id: entry.result.set_id, status: 'queued' }
    },

    async setStatus(id, signal) {
      checkSignal(signal)
      const entry = getSet(id)
      const progress = setState(entry, Date.now())
      if (progress.status === 'completed' && personalBaseline === null) personalBaseline = buildBaseline(entry)
      return { set_id: entry.result.set_id, ...progress }
    },

    async setResult(id, signal) {
      checkSignal(signal)
      const entry = getSet(id)
      const result = publicSet(entry, Date.now())
      if (result.status !== 'completed') throw demoError(409, 'SET_PROCESSING', '세트 분석이 진행 중이에요.')
      if (personalBaseline === null) personalBaseline = buildBaseline(entry)
      return result
    },

    async endSession(id, signal) {
      checkSignal(signal)
      const session = getSession(id)
      const now = Date.now()
      if (session.sets.some((set) => setState(set, now).status !== 'completed')) {
        throw demoError(409, 'SET_PROCESSING', '세트 분석이 끝난 뒤 운동을 종료해 주세요.')
      }
      session.endedAt ??= now
      return publicSession(session, now)
    },

    async progress(signal) {
      checkSignal(signal)
      const items = completedSessions().slice(0, 8).reverse()
        .filter((session) => session.sets.length > 0)
        .map((session) => ({
          date: new Date(session.endedAt).toISOString(),
          change_score: Number((session.sets.reduce((sum, entry) => sum + entry.result.change_score, 0) / session.sets.length).toFixed(2)),
        }))
      return { items }
    },

    async me(signal) {
      checkSignal(signal)
      return { ...profile }
    },

    async updateMe({ nickname }) {
      if (!nickname?.trim()) throw demoError(400, 'NICKNAME_REQUIRED', '닉네임을 입력해 주세요.')
      profile.nickname = nickname.trim()
      return { ...profile }
    },

    async createBaseline({ set_id } = {}) {
      const now = Date.now()
      const entry = set_id
        ? getSet(set_id)
        : runs.filter((session) => !session.id.startsWith('sample-'))
          .flatMap((session) => session.sets.toReversed())
          .find((set) => setState(set, now).status === 'completed')

      if (!entry || setState(entry, now).status !== 'completed') {
        throw demoError(400, 'BASELINE_SET_REQUIRED', '기준 동작으로 쓸 세트를 먼저 분석해 주세요.')
      }

      personalBaseline = buildBaseline(entry)
      return { ...personalBaseline }
    },
  }
}
