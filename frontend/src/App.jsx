import { useEffect, useMemo, useRef, useState } from 'react'
import { createApi } from './api.js'
import { createDemoApi } from './demoApi.js'
import { fromField, listFrom, unwrap } from './core/response.js'
import AuthScreen from './auth/AuthScreen.jsx'
import HomeScreen from './workouts/HomeScreen.jsx'
import SetInputScreen from './workouts/SetInputScreen.jsx'
import AnalysisScreen from './workouts/AnalysisScreen.jsx'
import SetResultScreen from './workouts/SetResultScreen.jsx'
import WorkoutSummaryScreen from './workouts/WorkoutSummaryScreen.jsx'
import WorkoutHistoryScreen from './workouts/WorkoutHistoryScreen.jsx'
import ProfileScreen from './users/ProfileScreen.jsx'
import { stages, VIDEO_LIMIT_BYTES } from './workouts/constants.js'
import { normalizeSetResult } from './workouts/result.js'
import { getSessionId, getSetId, getSets, isFailed, isReady, statusOf } from './workouts/session.js'
import './App.css'

const tokenKey = 'formfit-access-token'
const tabs = [
  ['home', '⌂', '홈'],
  ['history', '▥', '기록'],
  ['profile', '◎', '내 정보'],
]

function App() {
  const [auth, setAuth] = useState(() => {
    const token = sessionStorage.getItem(tokenKey)
    return token ? { token, demo: false } : null
  })
  const [screen, setScreen] = useState(auth ? 'home' : 'login')
  const [pending, setPending] = useState(false)
  const [loading, setLoading] = useState(false)
  const [actionError, setActionError] = useState('')
  const [pageError, setPageError] = useState('')
  const [reload, setReload] = useState(0)
  const [credentials, setCredentials] = useState({ nickname: '', email: '', password: '' })
  const [active, setActive] = useState(null)
  const [history, setHistory] = useState([])
  const [progressPoints, setProgressPoints] = useState([])
  const [profile, setProfile] = useState(null)
  const [baseline, setBaseline] = useState(null)
  const [editingProfile, setEditingProfile] = useState(false)
  const [nickname, setNickname] = useState('')
  const [showGuide, setShowGuide] = useState(false)
  const [video, setVideo] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [videoState, setVideoState] = useState('empty')
  const [videoError, setVideoError] = useState('')
  const [target, setTarget] = useState(15)
  const [rpe, setRpe] = useState(null)
  const [setNumber, setSetNumber] = useState(1)
  const [setId, setSetId] = useState(null)
  const [analysisStep, setAnalysisStep] = useState(0)
  const [analysisError, setAnalysisError] = useState('')
  const [pollRetry, setPollRetry] = useState(0)
  const [result, setResult] = useState(null)
  const [summary, setSummary] = useState(null)
  const [summaryBack, setSummaryBack] = useState('home')
  const main = useRef(null)
  const fileInput = useRef(null)
  const api = useMemo(() => auth?.demo ? createDemoApi() : createApi({ token: auth?.token }), [auth])

  function go(next) {
    setActionError('')
    setPageError('')
    setEditingProfile(false)
    setShowGuide(false)
    setScreen(next)
  }

  function logout() {
    sessionStorage.removeItem(tokenKey)
    setAuth(null)
    setCredentials({ nickname: '', email: '', password: '' })
    setActive(null)
    setHistory([])
    setProgressPoints([])
    setProfile(null)
    setBaseline(null)
    setSummary(null)
    setResult(null)
    setSetId(null)
    setAnalysisError('')
    setLoading(false)
    clearSetInputs()
    go('login')
  }

  useEffect(() => {
    if (screen !== 'login' && screen !== 'signup') main.current?.focus()
    window.scrollTo(0, 0)
  }, [screen])

  async function perform(callback, fallback) {
    if (pending) return
    setPending(true)
    setActionError('')
    try {
      await callback()
    } catch (error) {
      if (auth && !auth.demo && error.status === 401) {
        logout()
        setActionError('로그인 세션이 만료됐어요. 다시 로그인해 주세요.')
      } else {
        setActionError(error.message || fallback)
      }
    } finally {
      setPending(false)
    }
  }

  useEffect(() => {
    if (!auth || !['home', 'history', 'profile'].includes(screen)) return

    const controller = new AbortController()
    const { signal } = controller
    const optional = (request) => request.catch((error) => {
      if ([404, 405, 501].includes(error.status)) return null
      throw error
    })

    async function loadPage() {
      setLoading(true)
      setPageError('')
      const requests = {
        home: () => [
          optional(api.currentSession(signal)),
          optional(api.baseline(signal)),
          api.sessions({ size: 2, signal }),
        ],
        history: () => [api.sessions({ signal }), optional(api.progress(signal))],
        profile: () => [api.me(signal), optional(api.baseline(signal))],
      }
      const replies = await Promise.allSettled(requests[screen]())
      if (signal.aborted) return
      if (!auth.demo && replies.some((item) => item.status === 'rejected' && item.reason.status === 401)) {
        logout()
        setActionError('로그인 세션이 만료됐어요. 다시 로그인해 주세요.')
        return
      }

      const value = (index) => unwrap(replies[index]?.value)
      if (screen === 'home') {
        setActive(fromField(value(0), 'session') ?? null)
        setBaseline(fromField(value(1), 'baseline') ?? null)
        setHistory(listFrom(value(2), 'sessions'))
      } else if (screen === 'history') {
        setHistory(listFrom(value(0), 'sessions'))
        setProgressPoints(listFrom(value(1), 'points'))
      } else {
        setProfile(fromField(value(0), 'user') ?? null)
        setBaseline(fromField(value(1), 'baseline') ?? null)
      }
      const failed = replies.find((item) => item.status === 'rejected')
      if (failed) setPageError(failed.reason.message || '데이터를 불러오지 못했어요.')
      setLoading(false)
    }

    loadPage()
    return () => controller.abort()
  }, [api, auth, screen, reload])

  useEffect(() => {
    if (!video) return
    const url = URL.createObjectURL(video)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [video])

  useEffect(() => {
    if (screen !== 'analyzing' || setId == null) return

    const controller = new AbortController()
    const timeout = window.setTimeout(() => {
      controller.abort()
      setAnalysisError('분석이 아직 끝나지 않았어요. 잠시 뒤 상태를 다시 확인해 주세요.')
    }, 120_000)
    let timer

    async function poll() {
      try {
        const data = unwrap(await api.setStatus(setId, controller.signal))
        if (controller.signal.aborted) return
        const status = statusOf(data)
        if (isFailed(status)) {
          window.clearTimeout(timeout)
          setAnalysisError(data?.message ?? data?.error?.message ?? '영상을 분석하지 못했어요. 전신이 보이는 측면 영상으로 다시 시도해 주세요.')
          return
        }

        if (isReady(status)) {
          const response = unwrap(await api.setResult(setId, controller.signal))
          if (controller.signal.aborted) return
          const analysis = fromField(response, 'result')
          if (!analysis || typeof analysis !== 'object' || Array.isArray(analysis)) throw new Error('서버에서 분석 결과를 받지 못했어요.')
          setResult(normalizeSetResult({ ...analysis, set_number: analysis.set_number ?? setNumber }))
          setScreen('result')
          return
        }

        const stage = Number.isInteger(data?.stage) ? Math.max(0, Math.min(stages.length - 1, data.stage)) : 1
        setAnalysisStep(status === 'queued' || status === 'pending' ? 0 : stage)
        timer = window.setTimeout(poll, 850)
      } catch (error) {
        if (controller.signal.aborted) return
        window.clearTimeout(timeout)
        if (!auth?.demo && error.status === 401) {
          logout()
          setActionError('로그인 세션이 만료됐어요. 다시 로그인해 주세요.')
          return
        }
        setAnalysisError(error.message || '분석 상태를 불러오지 못했어요.')
      }
    }

    setAnalysisError('')
    poll()
    return () => {
      controller.abort()
      window.clearTimeout(timer)
      window.clearTimeout(timeout)
    }
  }, [api, auth, pollRetry, screen, setId, setNumber])

  function clearSetInputs() {
    setVideo(null)
    setPreviewUrl('')
    setVideoState('empty')
    setVideoError('')
    setRpe(null)
    if (fileInput.current) fileInput.current.value = ''
  }

  function enterInput(number) {
    clearSetInputs()
    setSetNumber(number)
    go('input')
  }

  function handleVideoChange(event) {
    const file = event.target.files[0]
    setVideo(null)
    setPreviewUrl('')
    setVideoState('empty')
    setVideoError('')
    if (!file) return
    if (!/\.(mp4|mov)$/i.test(file.name)) {
      setVideoError('MP4 또는 MOV 파일을 선택해 주세요.')
      event.target.value = ''
      return
    }
    if (file.size > VIDEO_LIMIT_BYTES || !file.size) {
      setVideoError(file.size ? '영상은 200MB 이하만 올릴 수 있어요.' : '비어 있는 파일은 올릴 수 없어요.')
      event.target.value = ''
      return
    }
    setVideo(file)
    setVideoState('checking')
  }

  function validateDuration(event) {
    const duration = event.currentTarget.duration
    if (!Number.isFinite(duration)) {
      setVideoState('server-check')
    } else if (duration < 3 || duration > 90) {
      setVideoState('invalid')
      setVideoError('영상 길이는 3~90초여야 해요.')
    } else {
      setVideoState('ready')
    }
  }

  function handleAuth(event) {
    event.preventDefault()
    perform(async () => {
      const login = { email: credentials.email.trim(), password: credentials.password }
      let data
      if (screen === 'signup') {
        data = unwrap(await api.signup({ ...login, nickname: credentials.nickname.trim() }))
      }
      if (!data?.access_token) data = unwrap(await api.login(login))
      if (!data?.access_token) throw new Error('로그인 응답에 access_token이 없어요.')
      sessionStorage.setItem(tokenKey, data.access_token)
      setAuth({ token: data.access_token, demo: false })
      setCredentials({ nickname: '', email: '', password: '' })
      go('home')
    }, '로그인에 실패했어요.')
  }

  function startDemo() {
    sessionStorage.removeItem(tokenKey)
    setCredentials({ nickname: '', email: '', password: '' })
    setAuth({ token: '', demo: true })
    go('home')
  }

  function startWorkout() {
    perform(async () => {
      if (active && getSessionId(active) != null) {
        const id = getSessionId(active)
        const response = unwrap(await api.session(id))
        const details = response?.session ?? response ?? active
        const sets = getSets(details)
        const latest = sets.at(-1)
        setActive({ ...active, ...details, session_id: id })
        setResult(null)
        if (latest && getSetId(latest) != null && !isFailed(statusOf(latest))) {
          if (Number.isInteger(latest.target_reps)) setTarget(latest.target_reps)
          setSetNumber(latest.set_number ?? sets.length)
          setSetId(getSetId(latest))
          setAnalysisStep(0)
          go('analyzing')
        } else {
          enterInput((details.set_count ?? sets.length) + 1)
        }
        return
      }

      const response = unwrap(await api.createSession())
      const session = response?.session ?? response
      if (getSessionId(session) == null) throw new Error('운동 시작 응답에 세션 ID가 없어요.')
      setActive(session)
      setTarget(15)
      setResult(null)
      enterInput(1)
    }, '운동을 시작하지 못했어요.')
  }

  function handleAnalyze(event) {
    event.preventDefault()
    if (!video || rpe === null || !['ready', 'server-check'].includes(videoState)) return
    analyzeSet({ video, rpe, target_reps: target })
  }

  function handleSampleAnalyze() {
    if (!auth?.demo) return
    analyzeSet({ use_sample: true, rpe: rpe ?? 3, target_reps: target })
  }

  function analyzeSet(payload) {
    perform(async () => {
      const response = unwrap(await api.uploadSet(getSessionId(active), payload))
      const data = response?.set ?? response
      if (getSetId(data) == null) throw new Error('업로드 응답에 세트 ID가 없어요.')
      setSetId(getSetId(data))
      setAnalysisStep(0)
      go('analyzing')
    }, '영상을 올리지 못했어요.')
  }

  function endWorkout() {
    perform(async () => {
      const id = getSessionId(active)
      if (!active?.ended) {
        await api.endSession(id)
        setActive({ ...active, ended: true })
      }
      const response = unwrap(await api.session(id))
      setSummary(response?.session ?? response)
      setActive(null)
      setSummaryBack('home')
      go('summary')
    }, '운동 요약을 불러오지 못했어요.')
  }

  function openWorkout(id) {
    perform(async () => {
      const response = unwrap(await api.session(id))
      setSummary(response?.session ?? response)
      setSummaryBack(screen)
      go('summary')
    }, '운동 기록을 불러오지 못했어요.')
  }

  function saveProfile(event) {
    event.preventDefault()
    if (!nickname.trim()) return
    perform(async () => {
      const response = unwrap(await api.updateMe({ nickname: nickname.trim() }))
      setProfile({ ...profile, nickname: nickname.trim(), ...(response?.user ?? response) })
      setEditingProfile(false)
    }, '프로필을 수정하지 못했어요.')
  }

  function rebuildBaseline() {
    perform(async () => {
      const completed = listFrom(await api.sessions({ size: 5 }), 'sessions')
        .find((item) => !['active', 'in_progress', 'ongoing'].includes(statusOf(item)))
      if (!completed || getSessionId(completed) == null) throw new Error('개인 기준으로 사용할 운동을 먼저 완료해 주세요.')
      const response = unwrap(await api.session(getSessionId(completed)))
      const set = getSets(response?.session ?? response).filter((item) => !isFailed(statusOf(item))).at(-1)
      if (getSetId(set) == null) throw new Error('개인 기준으로 사용할 분석 완료 세트가 없어요.')
      await api.createBaseline({ set_id: getSetId(set) })
      const data = unwrap(await api.baseline())
      setBaseline(fromField(data, 'baseline') ?? null)
    }, '개인 기준을 다시 만들지 못했어요.')
  }

  const authScreen = screen === 'login' || screen === 'signup'
  const tabScreen = tabs.some(([key]) => key === screen)
  const readyVideo = ['ready', 'server-check'].includes(videoState)

  return (
    <div className="coach-app">
      <main key={screen} data-screen={screen} className={`coach-content coach-content--${authScreen ? 'auth' : screen}`} ref={main} tabIndex={-1}>
        {authScreen && (
          <AuthScreen
            screen={screen}
            credentials={credentials}
            setCredentials={setCredentials}
            handleAuth={handleAuth}
            actionError={actionError}
            pending={pending}
            go={go}
            startDemo={startDemo}
          />
        )}

        {!authScreen && (
          <>
            <div className="app-topline"><span>FormFit</span></div>
            {actionError && <p className="notice notice--error" role="alert">{actionError}</p>}
            {pageError && (
              <div className="notice notice--error" role="alert">
                <p>{pageError}</p>
                <button className="text-button" type="button" onClick={() => setReload(reload + 1)}>다시 불러오기</button>
              </div>
            )}
            {loading && tabScreen && <p className="muted" role="status">불러오는 중…</p>}
          </>
        )}

        {screen === 'home' && (
          <HomeScreen
            pending={pending}
            loading={loading}
            startWorkout={startWorkout}
            active={active}
            baseline={baseline}
            go={go}
            history={history}
            openWorkout={openWorkout}
          />
        )}

        {screen === 'input' && (
          <SetInputScreen
            pending={pending}
            go={go}
            result={result}
            setNumber={setNumber}
            handleAnalyze={handleAnalyze}
            video={video}
            fileInput={fileInput}
            handleVideoChange={handleVideoChange}
            previewUrl={previewUrl}
            videoState={videoState}
            validateDuration={validateDuration}
            setVideoState={setVideoState}
            videoError={videoError}
            demo={auth?.demo}
            handleSampleAnalyze={handleSampleAnalyze}
            target={target}
            setTarget={setTarget}
            rpe={rpe}
            setRpe={setRpe}
          />
        )}

        {screen === 'analyzing' && (
          <AnalysisScreen
            analysisError={analysisError}
            setNumber={setNumber}
            demo={auth?.demo}
            analysisStep={analysisStep}
          />
        )}

        {screen === 'result' && result && (
          <SetResultScreen
            result={result}
            setNumber={setNumber}
            demo={auth?.demo}
            target={target}
            rpe={rpe}
          />
        )}

        {screen === 'summary' && (
          <WorkoutSummaryScreen
            summary={summary}
            demo={auth?.demo}
            summaryBack={summaryBack}
          />
        )}

        {screen === 'history' && (
          <WorkoutHistoryScreen
            progressPoints={progressPoints}
            history={history}
            openWorkout={openWorkout}
          />
        )}

        {screen === 'profile' && (
          <ProfileScreen
            profile={profile}
            pending={pending}
            setNickname={setNickname}
            setEditingProfile={setEditingProfile}
            editingProfile={editingProfile}
            saveProfile={saveProfile}
            nickname={nickname}
            baseline={baseline}
            loading={loading}
            rebuildBaseline={rebuildBaseline}
            showGuide={showGuide}
            setShowGuide={setShowGuide}
            logout={logout}
            demo={auth?.demo}
          />
        )}
      </main>

      {tabScreen && (
        <nav className="tab-bar" aria-label="하단 메뉴">
          {tabs.map(([key, icon, label]) => (
            <button key={key} type="button" disabled={pending} aria-current={screen === key ? 'page' : undefined} onClick={() => { if (screen !== key) go(key) }}>
              <span className="tab-icon" aria-hidden="true">{icon}</span>{label}
            </button>
          ))}
        </nav>
      )}
      {screen === 'input' && (
        <footer className="action-bar">
          <button className="coach-button" type="submit" form="set-form" disabled={pending || !readyVideo || rpe === null}>
            {pending ? '업로드 중…' : '분석하기'}
          </button>
        </footer>
      )}
      {screen === 'analyzing' && analysisError && (
        <footer className="action-bar action-bar--split">
          <button className="coach-button coach-button--secondary" type="button" onClick={() => enterInput(setNumber)}>영상 다시 선택</button>
          <button className="coach-button" type="button" onClick={() => setPollRetry(pollRetry + 1)}>상태 다시 확인</button>
        </footer>
      )}
      {screen === 'result' && (
        <footer className="action-bar action-bar--split">
          <button className="coach-button coach-button--secondary" type="button" disabled={pending} onClick={endWorkout}>{pending ? '처리 중…' : '운동 종료'}</button>
          <button className="coach-button" type="button" disabled={pending || active?.ended} onClick={() => {
            if (Number.isInteger(result?.next_target_reps) && result.next_target_reps > 0 && result.next_target_reps <= 99) setTarget(result.next_target_reps)
            enterInput((result?.set_number ?? setNumber) + 1)
          }}>다음 세트</button>
        </footer>
      )}
      {screen === 'summary' && (
        <footer className="action-bar">
          <button className="coach-button" type="button" onClick={() => go(summaryBack)}>{summaryBack === 'history' ? '기록으로' : '홈으로'}</button>
        </footer>
      )}
    </div>
  )
}

export default App
