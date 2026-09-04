import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Products from '../views/Products.vue'
import Orders from '../views/Orders.vue'
import Users from '../views/Users.vue'
import AIChat from '../views/AIChat.vue'
import Login from '../views/Login.vue'
import KnowledgeBase from '../views/KnowledgeBase.vue'
import KnowledgeDocuments from '../views/KnowledgeDocuments.vue'
import Roles from '../views/Roles.vue'
import Permissions from '../views/Permissions.vue'
import Categories from '../views/Categories.vue'
import AfterSales from '../views/AfterSales.vue'
import Coupons from '../views/Coupons.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { title: '登录', noAuth: true } },
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { title: '数据概览', requiresAuth: true } },
  { path: '/products', name: 'Products', component: Products, meta: { title: '商品管理', requiresAuth: true } },
  { path: '/orders', name: 'Orders', component: Orders, meta: { title: '订单管理', requiresAuth: true } },
  { path: '/users', name: 'Users', component: Users, meta: { title: '用户管理', requiresAuth: true } },
  { path: '/categories', name: 'Categories', component: Categories, meta: { title: '分类管理', requiresAuth: true } },
  { path: '/coupons', name: 'Coupons', component: Coupons, meta: { title: '优惠券管理', requiresAuth: true } },
  { path: '/after-sales', name: 'AfterSales', component: AfterSales, meta: { title: '售后管理', requiresAuth: true } },
  { path: '/knowledge-base', name: 'KnowledgeBase', component: KnowledgeBase, meta: { title: '知识库管理', requiresAuth: true } },
  { path: '/knowledge-base/:id/documents', name: 'KnowledgeDocuments', component: KnowledgeDocuments, meta: { title: '知识库文档', requiresAuth: true } },
  { path: '/roles', name: 'Roles', component: Roles, meta: { title: '角色管理', requiresAuth: true } },
  { path: '/permissions', name: 'Permissions', component: Permissions, meta: { title: '权限管理', requiresAuth: true } },
  { path: '/ai-chat', name: 'AIChat', component: AIChat, meta: { title: 'AI 助手', requiresAuth: true } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router