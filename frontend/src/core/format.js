export function numberLabel(value, unit = '', digits = 0) {
  return typeof value === 'number' && Number.isFinite(value) ? value.toFixed(digits) + unit : '—'
}

export function timeLabel(value) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) return '—'
  const seconds = Math.floor(value)
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
}

export function dateLabel(value) {
  const date = value ? new Date(value) : null
  return date && !Number.isNaN(date.getTime())
    ? new Intl.DateTimeFormat('ko-KR', { month: 'numeric', day: 'numeric', weekday: 'short' }).format(date)
    : '운동 기록'
}
