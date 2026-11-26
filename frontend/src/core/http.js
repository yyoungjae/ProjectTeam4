const errorMessages = {
  400: '입력값을 확인해 주세요.',
  401: '로그인 정보를 확인하거나 다시 로그인해 주세요.',
  404: '요청한 데이터를 찾을 수 없어요.',
  409: '현재 상태에서 이 요청을 처리할 수 없어요.',
  413: '영상은 200MB 이하로 올려주세요.',
  422: '입력한 항목의 형식을 확인해 주세요.',
}

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'UNKNOWN_ERROR', cause } = {}) {
    super(message, { cause })
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

function normalizeBaseUrl(baseUrl) {
  const base = (baseUrl || '/api').trim().replace(/\/+$/, '')
  if (/^https?:\/\/[^/]+$/i.test(base)) return base + '/api'
  return base || '/api'
}

export function createRequest({ token = '', baseUrl = import.meta.env?.VITE_API_BASE_URL } = {}) {
  const base = normalizeBaseUrl(baseUrl)

  async function request(path, { method = 'GET', body, auth = true, signal } = {}) {
    const headers = { Accept: 'application/json' }

    if (auth && token) headers.Authorization = 'Bearer ' + token

    let requestBody
    if (body instanceof FormData) {
      requestBody = body
    } else if (body !== undefined) {
      headers['Content-Type'] = 'application/json'
      requestBody = JSON.stringify(body)
    }

    let response
    try {
      response = await fetch(base + path, { method, headers, body: requestBody, signal })
    } catch (error) {
      if (signal?.aborted || error?.name === 'AbortError') throw error
      throw new ApiError('서버에 연결할 수 없어요. 백엔드 서버가 실행 중인지 확인해 주세요.', {
        code: 'NETWORK_ERROR',
        cause: error,
      })
    }

    if (response.status === 204) return null

    let raw
    try {
      raw = await response.text()
    } catch (error) {
      if (signal?.aborted || error?.name === 'AbortError') throw error
      throw new ApiError('서버 응답을 읽을 수 없어요. 다시 시도해 주세요.', {
        status: response.status,
        code: 'RESPONSE_READ_ERROR',
        cause: error,
      })
    }

    let data = null
    let invalidJson = false
    if (raw.trim()) {
      try {
        data = JSON.parse(raw)
      } catch {
        invalidJson = true
      }
    }

    if (!response.ok) {
      const serverMessage = typeof data?.message === 'string' ? data.message : null
      const serverCode = typeof data?.code === 'string' ? data.code : null
      throw new ApiError(serverMessage || errorMessages[response.status] || '요청을 처리하지 못했어요.', {
        status: response.status,
        code: serverCode || 'HTTP_' + response.status,
      })
    }

    if (invalidJson) {
      throw new ApiError('서버가 JSON 대신 다른 형식으로 응답했어요. API 주소를 확인해 주세요.', {
        status: response.status,
        code: 'INVALID_RESPONSE',
      })
    }

    return data
  }

  return request
}
