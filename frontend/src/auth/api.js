export function createAuthApi(request) {
  return {
    signup: (payload, signal) => request('/auth/signup', { method: 'POST', body: payload, auth: false, signal }),
    login: (payload, signal) => request('/auth/login', { method: 'POST', body: payload, auth: false, signal }),
  }
}
