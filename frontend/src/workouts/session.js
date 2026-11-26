export const getSessionId = (value) => value?.session_id ?? value?.id
export const getSetId = (value) => value?.set_id ?? value?.id
export const getSets = (value) => Array.isArray(value?.sets) ? value.sets : []
export const statusOf = (value) => String(value?.status ?? value?.analysis_status ?? '').toLowerCase()
export const isReady = (status) => ['completed', 'done', 'success', 'succeeded', 'finished', 'ready'].includes(status)
export const isFailed = (status) => ['failed', 'error', 'cancelled', 'canceled'].includes(status)


export function sessionStats(session) {
  const sets = getSets(session)
  const knownReps = sets.filter((set) => typeof set.rep_count === 'number')
  return {
    sets: session?.set_count ?? (sets.length || null),
    reps: session?.total_reps ?? (knownReps.length ? knownReps.reduce((sum, set) => sum + set.rep_count, 0) : null),
    duration: session?.duration_seconds ?? null,
  }
}
