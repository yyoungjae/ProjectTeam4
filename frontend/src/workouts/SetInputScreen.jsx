import { effortLabels } from "./constants.js"

export default function SetInputScreen({
  pending,
  go,
  result,
  setNumber,
  handleAnalyze,
  video,
  fileInput,
  handleVideoChange,
  previewUrl,
  videoState,
  validateDuration,
  setVideoState,
  videoError,
  demo,
  handleSampleAnalyze,
  target,
  setTarget,
  rpe,
  setRpe,
}) {
  return (
    <>
      <header className="screen-header screen-header--back">
        <button className="back-button" type="button" aria-label="이전 화면" disabled={pending}
          onClick={() => go(result ? 'result' : 'home')}>‹</button>
        <h1>{setNumber}세트</h1>
      </header>
      <form id="set-form" className="screen-stack" onSubmit={handleAnalyze}>
        <section className="surface video-guide">
          <h2>촬영 가이드</h2>
          <ul className="guide-list">
            <li>몸 전체가 보이게 옆에서 촬영하세요.</li>
            <li>MP4·MOV, 3~90초, 200MB 이하</li>
          </ul>
        </section>
        <div className="video-panel">
          <label className="video-picker">
            <span className="upload-symbol" aria-hidden="true">↑</span>
            <strong>{video ? '영상 바꾸기' : '영상 파일 선택'}</strong>
            {video && <span className="video-picker-name">{video.name}</span>}
            <input type="file" accept=".mp4,.mov,video/mp4,video/quicktime" ref={fileInput}
              aria-label="스쿼트 영상 파일" disabled={pending} onChange={handleVideoChange} />
          </label>
          {previewUrl && videoState !== 'server-check' && (
            <video key={previewUrl} src={previewUrl} controls playsInline preload="metadata"
              aria-label="선택한 영상 미리보기" onLoadedMetadata={validateDuration}
              onError={() => setVideoState((state) => state === 'invalid' ? state : 'server-check')} />
          )}
          {videoState === 'checking' && <p className="preview-message" role="status">영상 길이를 확인하고 있어요.</p>}
          {videoState === 'server-check' && <p className="preview-message" role="status">브라우저에서 미리 볼 수 없어요. 파일은 선택되어 있습니다.</p>}
          {videoError && <p className="notice notice--error" role="alert">{videoError}</p>}
          {demo && (
            <div className="preview-message">
              <button className="text-button" type="button" disabled={pending} onClick={handleSampleAnalyze}>
                영상 없이 시연
              </button>
            </div>
          )}
        </div>
        <section className="surface target-row">
          <div><h2>목표 횟수</h2><p className="muted">이번 세트에서 하려는 횟수</p></div>
          <div className="stepper">
            <button type="button" aria-label="목표 횟수 줄이기" disabled={pending || target <= 1} onClick={() => setTarget(target - 1)}>−</button>
            <output aria-label="목표 횟수">{target}</output>
            <button type="button" aria-label="목표 횟수 늘리기" disabled={pending || target >= 99} onClick={() => setTarget(target + 1)}>+</button>
          </div>
        </section>
        <fieldset className="surface fatigue-card" disabled={pending}>
          <legend className="sr-only">체감 피로도</legend>
          <h2>방금 세트, 얼마나 힘들었나요?</h2>
          <p className="muted">휴식 시간 추천에 사용하는 값이에요.</p>
          <div className="fatigue-scale">
            {effortLabels.map((label, index) => (
              <label key={label}>
                <input type="radio" name="rpe" value={index + 1} checked={rpe === index + 1}
                  onChange={() => setRpe(index + 1)} />
                <span><strong>{index + 1}</strong><small>{label}</small></span>
              </label>
            ))}
          </div>
        </fieldset>
      </form>
    </>
  )
}
