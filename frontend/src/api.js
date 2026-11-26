import { createRequest } from './core/http.js'
import { createAuthApi } from './auth/api.js'
import { createUsersApi } from './users/api.js'
import { createWorkoutApi } from './workouts/api.js'

export { ApiError } from './core/http.js'

export function createApi(options) {
  const request = createRequest(options)

  return {
    health: (signal) => request('/health', { auth: false, signal }),
    ...createAuthApi(request),
    ...createUsersApi(request),
    ...createWorkoutApi(request),
  }
}
