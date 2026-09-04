import api from './index.js'

export function searchProducts(keyword) {
  return api.get('/api/products', { params: { keyword: keyword || '' } })
}

export function getProduct(id) {
  return api.get(`/api/products/${id}`)
}