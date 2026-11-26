import { dateLabel, numberLabel, timeLabel } from "../core/format.js"
import { getSets, sessionStats } from "./session.js"
import { ScoreChart } from "./components.jsx"

export default function WorkoutSummaryScreen({
  summary,
  demo,
  summaryBack,
}) {
  const stats = sessionStats(summary)

  return (
    <>
      <header className="screen-header">
        <p className="muted">{dateLabel(summary?.started_at ?? summary?.created_at)}{demo ? ' · 예시 데이터' : ''}</p>
        <h1>{summaryBack === 'home' ? '오늘 운동 완료' : '운동 요약'}</h1>
      </header>
      <dl className="summary-stats">
        <div className="surface"><dt>세트</dt><dd>{numberLabel(stats.sets)}</dd></div>
        <div className="surface"><dt>총 횟수</dt><dd>{numberLabel(stats.reps, '회')}</dd></div>
        <div className="surface"><dt>운동 시간</dt><dd>{timeLabel(stats.duration)}</dd></div>
      </dl>
      <section className="surface">
        <h2>세트별 동작 변화 점수</h2>
        <ScoreChart points={getSets(summary).map((set, index) => ({ label: `${set.set_number ?? index + 1}세트`, value: set.change_score }))} />
      </section>
    </>
  )
}
