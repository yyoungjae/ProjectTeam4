import { dateLabel, numberLabel } from "../core/format.js"

export default function ProfileScreen({
  profile,
  pending,
  setNickname,
  setEditingProfile,
  editingProfile,
  saveProfile,
  nickname,
  baseline,
  loading,
  rebuildBaseline,
  showGuide,
  setShowGuide,
  logout,
  demo,
}) {
  return (
    <>
      <header className="screen-header"><h1>내 정보</h1></header>
      <div className="screen-stack">
        {profile && (
          <section className="surface screen-stack">
            <div className="profile-row">
              <span className="avatar" aria-hidden="true">{(profile.nickname || '?').slice(0, 1)}</span>
              <div><h2>{profile.nickname || '사용자'}</h2><p className="muted">{profile.email}</p></div>
              <button className="text-button" type="button" disabled={pending}
                onClick={() => { setNickname(profile.nickname ?? ''); setEditingProfile(!editingProfile) }}>
                {editingProfile ? '취소' : '수정'}
              </button>
            </div>
            {editingProfile && (
              <form className="screen-stack" onSubmit={saveProfile}>
                <label className="field"><span>닉네임</span><input value={nickname} onChange={(event) => setNickname(event.target.value)} required /></label>
                <button className="coach-button" type="submit" disabled={pending || !nickname.trim()}>{pending ? '저장 중…' : '저장'}</button>
              </form>
            )}
          </section>
        )}
        <section className="surface screen-stack">
          <div><h2>개인 기준 동작</h2><p className="muted">{baseline ? dateLabel(baseline.created_at) + '에 만든 기준이에요.' : '기준으로 쓸 운동을 먼저 완료해 주세요.'}</p></div>
          {baseline && (
            <dl className="baseline-metrics">
              <div><dt>최저 무릎 각도</dt><dd>{numberLabel(baseline.min_knee_angle, '°', 1)}</dd></div>
              <div><dt>상체 기울기</dt><dd>{numberLabel(baseline.torso_angle, '°', 1)}</dd></div>
              <div><dt>반복 시간</dt><dd>{numberLabel(baseline.duration_sec, '초', 2)}</dd></div>
            </dl>
          )}
          <button className="coach-button coach-button--secondary" type="button" disabled={pending || loading} onClick={rebuildBaseline}>
            {pending ? '처리 중…' : baseline ? '기준 다시 만들기' : '개인 기준 만들기'}
          </button>
        </section>
        <section className="surface profile-actions">
          <button className="text-button" type="button" aria-expanded={showGuide} onClick={() => setShowGuide(!showGuide)}>촬영 가이드 {showGuide ? '닫기' : '보기'}</button>
          {showGuide && <p className="muted">몸 전체가 보이도록 측면에서 찍은 3~90초 길이의 MP4 또는 MOV 영상을 준비하세요.</p>}
        </section>
        <button className="coach-button coach-button--secondary" type="button" disabled={pending} onClick={logout}>{demo ? '시연 종료' : '로그아웃'}</button>
      </div>
    </>
  )
}
