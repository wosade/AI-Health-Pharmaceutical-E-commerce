import api from './index.js'

export function getOrdersByUser(userId) {
  return api.get('/api/orders', { params: { userId } })
}

export function getOrderByNo(orderNo) {
  return api.get(`/api/orders/${orderNo}`)
}

export function getOrdersByStatus(status) {
  return api.get(`/api/orders/status/${status}`)
}