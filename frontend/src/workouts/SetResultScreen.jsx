import { numberLabel, timeLabel } from "../core/format.js"
import { effortLabels } from "./constants.js"

export default function SetResultScreen({
  result,
  setNumber,
  demo,
  target,
  rpe,
}) {
  const { reps: resultReps, feedback } = result
  const hasKneeAngle = resultReps.some((rep) => Number.isFinite(rep.min_knee_angle))
  const hasThighAngle = resultReps.some((rep) => Number.isFinite(rep.min_thigh_angle))

  return (
    <>
      <header className="screen-header">
        <p className="muted">{result.set_number ?? setNumber}세트 결과{demo ? ' · 예시 데이터' : ''}</p>
        <h1>{numberLabel(result.rep_count ?? (resultReps.length || null), '회')} <small>/ 목표 {numberLabel(result.target_reps ?? target, '회')}</small></h1>
        {(result.rpe ?? rpe) != null && <p className="muted">피로도 {result.rpe ?? rpe} · {effortLabels[(result.rpe ?? rpe) - 1]}</p>}
      </header>
      <div className="screen-stack">
        {feedback.map((item, index) => (
          <section className="surface feedback-card" key={index}>
            <span className="score-tag" aria-hidden="true">{index + 1}</span>
            <div><h2>{item.title ?? (typeof item === 'string' ? item : '동작 피드백')}</h2>{item.message && <p className="muted">{item.message}</p>}</div>
          </section>
        ))}
        <section className="surface analysis-card">
          <h2>반복별 분석</h2>
          {resultReps.length ? (
            <table className="rep-table">
              <thead>
                <tr>
                  <th scope="col">반복</th>
                  {hasKneeAngle && <th scope="col">최저 무릎 각도</th>}
                  {hasThighAngle && <th scope="col">최저 허벅지 각도</th>}
                  <th scope="col">소요 시간</th>
                </tr>
              </thead>
              <tbody>{resultReps.map((rep, index) => (
                <tr key={rep.rep_index ?? index}>
                  <th scope="row">{rep.rep_index ?? index + 1}회</th>
                  {hasKneeAngle && <td>{numberLabel(rep.min_knee_angle, '°', 1)}</td>}
                  {hasThighAngle && <td>{numberLabel(rep.min_thigh_angle, '°', 1)}</td>}
                  <td>{numberLabel(rep.duration_sec, '초', 2)}</td>
                </tr>
              ))}</tbody>
            </table>
          ) : <p className="muted">표시할 반복별 결과가 없어요.</p>}
        </section>
        <section className="rest-card">
          <div><p>추천 휴식</p><strong>{timeLabel(result.recommended_rest_seconds)}</strong></div>
          <div><p>다음 세트 목표</p><strong>{numberLabel(result.next_target_reps, '회')}</strong></div>
        </section>
      </div>
    </>
  )
}
