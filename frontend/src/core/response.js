export const fromField = (value, key) => value && Object.hasOwn(value, key) ? value[key] : value
export const unwrap = (value) => fromField(value, 'data')

export function listFrom(value, key) {
  const data = unwrap(value)
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.items)) return data.items
  return Array.isArray(data?.[key]) ? data[key] : []
}
