<template>
  <aside class="sidebar">
    <div class="logo-area">
      <img class="logo-img" src="https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg" alt="logo" />
      <h1 class="logo-title">药智通</h1>
    </div>
    <a-menu
      mode="inline"
      theme="dark"
      :selected-keys="[currentPath]"
      :open-keys="openKeys"
      class="nav-menu"
      @click="handleMenuClick"
      @update:openKeys="openKeys = $event"
    >
      <a-menu-item v-for="item in topMenus" :key="item.path">
        <template #icon><component :is="item.icon" /></template>
        <span>{{ item.label }}</span>
      </a-menu-item>

      <a-sub-menu key="mall">
        <template #icon><ShopOutlined /></template>
        <template #title>商城管理</template>
        <a-menu-item v-for="item in mallMenus" :key="item.path">
          <template #icon><component :is="item.icon" /></template>
          <span>{{ item.label }}</span>
        </a-menu-item>
      </a-sub-menu>

      <a-sub-menu key="system">
        <template #icon><SettingOutlined /></template>
        <template #title>系统管理</template>
        <a-menu-item v-for="item in sysMenus" :key="item.path">
          <template #icon><component :is="item.icon" /></template>
          <span>{{ item.label }}</span>
        </a-menu-item>
      </a-sub-menu>

      <a-sub-menu key="ai">
        <template #icon><RobotOutlined /></template>
        <template #title>AI 智能</template>
        <a-menu-item v-for="item in aiMenus" :key="item.path">
          <template #icon><component :is="item.icon" /></template>
          <span>{{ item.label }}</span>
        </a-menu-item>
      </a-sub-menu>
    </a-menu>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DashboardOutlined,
  MedicineBoxOutlined,
  OrderedListOutlined,
  UserOutlined,
  RobotOutlined,
  ShopOutlined,
  SettingOutlined,
  AppstoreOutlined,
  TagOutlined,
  GiftOutlined,
  SafetyOutlined,
  KeyOutlined,
  DatabaseOutlined,
  FileTextOutlined,
} from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()

const openKeys = ref(['mall', 'system', 'ai'])

const topMenus = [
  { path: '/', label: '数据概览', icon: DashboardOutlined },
]

const mallMenus = [
  { path: '/products', label: '商品管理', icon: MedicineBoxOutlined },
  { path: '/orders', label: '订单管理', icon: OrderedListOutlined },
  { path: '/categories', label: '分类管理', icon: AppstoreOutlined },
  { path: '/coupons', label: '优惠券管理', icon: GiftOutlined },
  { path: '/after-sales', label: '售后管理', icon: SafetyOutlined },
]

const sysMenus = [
  { path: '/users', label: '用户管理', icon: UserOutlined },
  { path: '/roles', label: '角色管理', icon: TagOutlined },
  { path: '/permissions', label: '权限管理', icon: KeyOutlined },
]

const aiMenus = [
  { path: '/ai-chat', label: 'AI 助手', icon: RobotOutlined },
  { path: '/knowledge-base', label: '知识库管理', icon: DatabaseOutlined },
]

const currentPath = computed(() => route.path)

const handleMenuClick = ({ key }) => {
  router.push(key)
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background: #001529;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  overflow: hidden;
}

.logo-area {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.logo-img {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  margin: 0;
}

.nav-menu {
  flex: 1;
  overflow-y: auto;
  border-inline-end: none !important;
}

.nav-menu.ant-menu-dark {
  background: #001529;
}

.nav-menu .ant-menu-item {
  margin: 2px 0;
  border-radius: 0;
  height: 40px;
  line-height: 40px;
}

.nav-menu .ant-menu-item-selected {
  background-color: #1890ff !important;
}
</style>