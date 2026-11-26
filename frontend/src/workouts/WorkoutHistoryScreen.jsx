import { dateLabel } from "../core/format.js"
import { ScoreChart, WorkoutList } from "./components.jsx"

export default function WorkoutHistoryScreen({
  progressPoints,
  history,
  openWorkout,
}) {
  return (
    <>
      <header className="screen-header"><h1>기록</h1></header>
      <div className="screen-stack">
        <section className="surface">
          <h2>운동별 평균 변화 점수</h2>
          <ScoreChart points={progressPoints.map((point) => ({
            label: dateLabel(point.date ?? point.started_at),
            value: point.change_score ?? point.avg_change_score,
          }))} />
        </section>
        <section className="recent-workout">
          <h2>지난 운동</h2>
          <WorkoutList sessions={history} onOpen={openWorkout} />
        </section>
      </div>
    </>
  )
}
