import api from './index.js'

export function searchUsers(keyword) {
  return api.get('/api/users', { params: { keyword: keyword || '' } })
}

export function getUser(id) {
  return api.get(`/api/users/${id}`)
}