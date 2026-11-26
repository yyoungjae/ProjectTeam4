import { listFrom } from '../core/response.js'

export function normalizeSetResult(result) {
  const { analysis, recommendation, verdict } = result
  const rawReps = analysis?.reps ?? result.reps ?? result.rep_details
  const reps = listFrom(rawReps, 'reps')
    .filter((rep) => rep && typeof rep === 'object')
    .map((rep) => ({
      ...rep,
      rep_index: rep.rep_index ?? rep.rep_no,
      duration_sec: rep.duration_sec ?? durationFromTimestamps(rep),
    }))
  const feedback = result.feedback ?? verdict?.feedback

  return {
    ...result,
    reps,
    feedback: Array.isArray(feedback) ? feedback.filter(Boolean) : [],
    rep_count: result.rep_count ?? analysis?.rep_count,
    recommended_rest_seconds: result.recommended_rest_seconds ?? result.rest_sec ?? recommendation?.rest_sec,
    next_target_reps: result.next_target_reps ?? recommendation?.next_target_reps,
  }
}

function durationFromTimestamps({ start_t, end_t }) {
  if (!Number.isFinite(start_t) || !Number.isFinite(end_t) || end_t < start_t) return undefined
  return end_t - start_t
}
