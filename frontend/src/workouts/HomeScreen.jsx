import { dateLabel } from "../core/format.js"
import { getSessionId } from "./session.js"
import { WorkoutList } from "./components.jsx"

export default function HomeScreen({
  pending,
  loading,
  startWorkout,
  active,
  baseline,
  go,
  history,
  openWorkout,
}) {
  return (
    <div className="screen-stack">
      <header className="screen-header">
        <h1>스쿼트 코치</h1>
        <p className="muted">오늘도 스쿼트 해볼까요?</p>
      </header>
      <section className="hero-card">
        <p className="eyebrow">템포 스쿼트</p>
        <h2>세트마다 측면 영상을 올리고 자세와 휴식 시간을 확인하세요</h2>
        <button className="coach-button coach-button--light" type="button" disabled={pending || loading} onClick={startWorkout}>
          {pending ? '불러오는 중…' : getSessionId(active) != null ? '운동 이어하기' : '운동 시작'}
        </button>
      </section>
      <section className="surface panel-heading">
        <div><h2>개인 기준 동작</h2><p className="muted">{baseline ? dateLabel(baseline.created_at) + ' 기준' : '아직 등록된 기준 동작이 없어요.'}</p></div>
        {baseline && <button className="text-button" type="button" disabled={pending} onClick={() => go('profile')}>보기</button>}
      </section>
      <section className="recent-workout">
        <div className="panel-heading"><h2>최근 운동</h2><button className="text-button" type="button" disabled={pending} onClick={() => go('history')}>전체 보기</button></div>
        <WorkoutList sessions={history.slice(0, 2)} onOpen={openWorkout} />
      </section>
    </div>
  )
}
