export function createUsersApi(request) {
  return {
    me: (signal) => request('/users/me', { signal }),
    updateMe: (payload, signal) => request('/users/me', { method: 'PATCH', body: payload, signal }),
  }
}
