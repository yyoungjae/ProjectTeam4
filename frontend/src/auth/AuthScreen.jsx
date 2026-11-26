export default function AuthScreen({
  screen,
  credentials,
  setCredentials,
  handleAuth,
  actionError,
  pending,
  go,
  startDemo,
}) {
  return (
    <>
      <header className="auth-brand">
        <div className="auth-mark" aria-hidden="true">F</div>
        <h1>{screen === 'signup' ? 'FormFit 회원가입' : '스쿼트 코치'}</h1>
        <p className="muted">영상으로 자세를 확인하고 다음 세트까지의 휴식 시간을 알아보세요.</p>
      </header>

      <form className="auth-form" onSubmit={handleAuth}>
        {screen === 'signup' && (
          <label className="field">
            <span>닉네임</span>
            <input value={credentials.nickname} autoComplete="nickname" required
              onChange={(event) => setCredentials({ ...credentials, nickname: event.target.value })} />
          </label>
        )}
        <label className="field">
          <span>이메일</span>
          <input type="email" placeholder="you@example.com" value={credentials.email} autoComplete="email" required
            onChange={(event) => setCredentials({ ...credentials, email: event.target.value })} />
        </label>
        <label className="field">
          <span>비밀번호</span>
          <input type="password" minLength={screen === 'signup' ? 8 : undefined}
            placeholder={screen === 'signup' ? '8자 이상' : '비밀번호 입력'}
            autoComplete={screen === 'signup' ? 'new-password' : 'current-password'} value={credentials.password} required
            onChange={(event) => setCredentials({ ...credentials, password: event.target.value })} />
        </label>
        {actionError && <p className="notice notice--error" role="alert">{actionError}</p>}
        <button className="coach-button" disabled={pending} type="submit">
          {pending ? '연결 중…' : screen === 'signup' ? '회원가입' : '로그인'}
        </button>
      </form>
      <div className="auth-switch">
        <button className="text-button" type="button" disabled={pending} onClick={() => go(screen === 'signup' ? 'login' : 'signup')}>
          {screen === 'signup' ? '이미 계정이 있나요? 로그인' : '처음이신가요? 회원가입'}
        </button>
        <button className="coach-button coach-button--secondary" type="button" disabled={pending} onClick={startDemo}>
          로그인 없이 시연 보기
        </button>
      </div>
    </>
  )
}
