import { ApiError } from '../core/http.js'
import { VIDEO_LIMIT_BYTES } from './constants.js'

function pathId(id) {
  if (id === null || id === undefined || String(id).trim() === '') {
    throw new ApiError('요청할 항목의 ID를 확인해 주세요.', { code: 'MISSING_ID' })
  }

  return encodeURIComponent(String(id))
}

function createSetFormData({ video, rpe, target_reps } = {}) {
  if (typeof File === 'undefined' || !(video instanceof File) || video.size === 0) {
    throw new ApiError('업로드할 영상 파일을 선택해 주세요.', { status: 400, code: 'VIDEO_REQUIRED' })
  }

  if (!/\.(mp4|mov)$/i.test(video.name)) {
    throw new ApiError('MP4 또는 MOV 영상을 선택해 주세요.', { status: 400, code: 'INVALID_VIDEO_FORMAT' })
  }

  if (video.size > VIDEO_LIMIT_BYTES) {
    throw new ApiError('영상은 200MB 이하로 올려주세요.', { status: 413, code: 'VIDEO_TOO_LARGE' })
  }

  const numericRpe = Number(rpe)
  if (!Number.isInteger(numericRpe) || numericRpe < 1 || numericRpe > 5) {
    throw new ApiError('체감 피로도는 1~5점 중에서 선택해 주세요.', { status: 400, code: 'INVALID_RPE' })
  }

  const formData = new FormData()
  formData.append('video', video)
  formData.append('rpe', String(numericRpe))

  if (target_reps !== undefined && target_reps !== null && target_reps !== '') {
    formData.append('target_reps', String(target_reps))
  }

  return formData
}

export function createWorkoutApi(request) {
  return {
    currentSession: (signal) => request('/sessions/current', { signal }),
    baseline: (signal) => request('/baseline', { signal }),
    sessions({ size, page, signal } = {}) {
      const query = new URLSearchParams()
      if (size !== undefined && size !== null) query.set('size', String(size))
      if (page !== undefined && page !== null) query.set('page', String(page))
      const search = query.toString()
      return request(search ? '/sessions?' + search : '/sessions', { signal })
    },
    createSession: (payload, signal) => request('/sessions', { method: 'POST', body: payload, signal }),
    session: (id, signal) => request('/sessions/' + pathId(id), { signal }),
    uploadSet: (id, payload, signal) => request('/sessions/' + pathId(id) + '/sets', {
      method: 'POST',
      body: createSetFormData(payload),
      signal,
    }),
    setStatus: (id, signal) => request('/sets/' + pathId(id) + '/status', { signal }),
    setResult: (id, signal) => request('/sets/' + pathId(id), { signal }),
    endSession: (id, signal) => request('/sessions/' + pathId(id) + '/end', { method: 'PATCH', signal }),
    progress: (signal) => request('/stats/progress', { signal }),
    createBaseline: (payload, signal) => request('/baseline', { method: 'POST', body: payload, signal }),
  }
}
