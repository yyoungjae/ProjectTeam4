import { stages } from "./constants.js"

export default function AnalysisScreen({
  analysisError,
  setNumber,
  demo,
  analysisStep,
}) {
  return (
    <>
      <header className="analysis-heading">
        {!analysisError && <div className="spinner" aria-hidden="true" />}
        <h1>{analysisError ? '분석 상태를 확인해 주세요' : `${setNumber}세트를 분석하고 있어요`}</h1>
        {!analysisError && <p className="muted">{demo ? '예시 데이터로 분석 흐름을 보여드려요.' : '분석이 끝나면 결과가 자동으로 열려요.'}</p>}
      </header>
      {!analysisError ? (
        <ol className="surface analysis-steps" aria-label="분석 진행 단계">
          {stages.map((stage, index) => (
            <li key={stage} className={index <= analysisStep ? 'step-reached' : ''}
              aria-current={index === analysisStep ? 'step' : undefined}>
              <span className={index < analysisStep ? 'step-dot step-dot--done' : 'step-dot'} aria-hidden="true">
                {index < analysisStep ? '✓' : ''}
              </span>{demo && index === 0 ? '예시 데이터 준비 완료' : stage}
            </li>
          ))}
        </ol>
      ) : <p className="notice notice--error" role="alert">{analysisError}</p>}
    </>
  )
}
