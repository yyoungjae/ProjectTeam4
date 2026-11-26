import { dateLabel, numberLabel, timeLabel } from '../core/format.js'
import { getSessionId, sessionStats } from './session.js'

export function WorkoutList({ sessions, onOpen }) {
  if (!sessions.length) return <p className="surface muted">완료된 운동 기록이 아직 없어요.</p>

  return (
    <div className="screen-stack">
      {sessions.map((item) => {
        const id = getSessionId(item)
        const stats = sessionStats(item)
        return (
          <button className="surface recent-workout-button" type="button" key={id}
            disabled={id == null} onClick={() => onOpen(id)}>
            <strong>{dateLabel(item.started_at ?? item.created_at)}</strong>
            <span>{numberLabel(stats.sets, '세트')} · 총 {numberLabel(stats.reps, '회')} · {timeLabel(stats.duration)}</span>
          </button>
        )
      })}
    </div>
  )
}

export function ScoreChart({ points }) {
  const measured = points.filter((point) => typeof point.value === 'number' && Number.isFinite(point.value))
  if (!measured.length) return <p className="muted">표시할 변화 점수가 아직 없어요.</p>

  const max = Math.max(...measured.map((point) => Math.abs(point.value)), 0.01)
  return (
    <div className="app-chart">
      <ol className="rep-chart">
        {measured.map((point, index) => (
          <li key={index}>
            <strong>{point.value.toFixed(2)}</strong>
            <span className="chart-bar" style={{ height: `${Math.max(4, Math.abs(point.value) / max * 86)}px` }} aria-hidden="true" />
            <span>{point.label}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}
