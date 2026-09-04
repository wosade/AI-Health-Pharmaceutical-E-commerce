<template>
  <div class="page-container">
    <a-card :bordered="false" class="search-card">
      <a-row :gutter="16" align="middle">
        <a-col :flex="1">
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索用户名/昵称/手机号..."
            enter-button="搜索"
            style="max-width: 360px"
            @search="doSearch"
          />
        </a-col>
        <a-col>
          <a-button type="primary" @click="doSearch">
            <template #icon><SearchOutlined /></template>
            查询
          </a-button>
          <a-button style="margin-left: 8px" @click="handleReset">
            <template #icon><ReloadOutlined /></template>
            重置
          </a-button>
        </a-col>
      </a-row>
    </a-card>

    <a-card :bordered="false" class="table-card">
      <a-table
        :columns="columns"
        :data-source="list"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        :row-selection="rowSelection"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'avatar'">
            <a-image
              v-if="record.avatar"
              :src="record.avatar"
              :width="40"
              :height="40"
              style="object-fit: cover; border-radius: 4px"
              :preview="{ mask: '预览' }"
            />
            <div v-else class="no-avatar">
              <UserOutlined />
            </div>
          </template>
          <template v-else-if="column.key === 'gender'">
            <span>{{ genderLabel(record.gender) }}</span>
          </template>
          <template v-else-if="column.key === 'createTime'">
            {{ formatTime(record.createTime) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a @click="handleDetail(record)">详情</a>
              <a @click="handleEdit(record)">编辑</a>
              <a-dropdown>
                <a class="more-action">更多 <DownOutlined /></a>
                <template #overlay>
                  <a-menu>
                    <a-menu-item @click="handleWallet(record)">
                      <WalletOutlined />
                      <span style="margin-left: 8px">钱包</span>
                    </a-menu-item>
                    <a-menu-divider />
                    <a-menu-item danger @click="handleDelete(record)">
                      <DeleteOutlined />
                      <span style="margin-left: 8px">删除</span>
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:open="detailVisible"
      title="用户详情"
      :footer="null"
      width="640px"
    >
      <a-descriptions v-if="currentUser" bordered :column="2" size="small">
        <a-descriptions-item label="用户名">{{ currentUser.username }}</a-descriptions-item>
        <a-descriptions-item label="昵称">{{ currentUser.nickname }}</a-descriptions-item>
        <a-descriptions-item label="真实姓名">{{ currentUser.realName || '-' }}</a-descriptions-item>
        <a-descriptions-item label="手机号">{{ currentUser.phoneNumber || '-' }}</a-descriptions-item>
        <a-descriptions-item label="邮箱">{{ currentUser.email || '-' }}</a-descriptions-item>
        <a-descriptions-item label="性别">{{ genderLabel(currentUser.gender) }}</a-descriptions-item>
        <a-descriptions-item label="角色">{{ currentUser.roles || '-' }}</a-descriptions-item>
        <a-descriptions-item label="注册时间">{{ formatTime(currentUser.createTime) }}</a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  SearchOutlined,
  ReloadOutlined,
  DownOutlined,
  UserOutlined,
  WalletOutlined,
  DeleteOutlined,
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { searchUsers } from '../api/users.js'

const keyword = ref('')
const list = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentUser = ref(null)
const selectedRowKeys = ref([])

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条`,
})

const rowSelection = {
  selectedRowKeys: selectedRowKeys,
  onChange: (keys) => { selectedRowKeys.value = keys },
}

const columns = [
  { title: '头像', key: 'avatar', width: 70 },
  { title: '用户名', dataIndex: 'username', ellipsis: true, width: 120 },
  { title: '昵称', dataIndex: 'nickname', ellipsis: true, width: 120 },
  { title: '真实姓名', dataIndex: 'realName', ellipsis: true, width: 100 },
  { title: '手机号', dataIndex: 'phoneNumber', width: 130 },
  { title: '邮箱', dataIndex: 'email', ellipsis: true, width: 160 },
  { title: '性别', key: 'gender', width: 70, align: 'center' },
  { title: '注册时间', key: 'createTime', width: 170 },
  { title: '操作', key: 'action', width: 200, fixed: 'right' },
]

function genderLabel(g) {
  if (g === 1) return '男'
  if (g === 2) return '女'
  return '未知'
}

async function doSearch() {
  loading.value = true
  try {
    const res = await searchUsers(keyword.value)
    if (res.code === 200) {
      const data = res.data || []
      list.value = data
      pagination.total = data.length
    }
  } finally {
    loading.value = false
  }
}

function handleReset() {
  keyword.value = ''
  doSearch()
}

function handleTableChange(pag) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
}

function handleDetail(record) {
  currentUser.value = record
  detailVisible.value = true
}

function handleEdit(record) {
  message.info(`编辑用户: ${record.nickname || record.username}`)
}

function handleWallet(record) {
  message.info(`查看用户 ${record.nickname || record.username} 的钱包`)
}

function handleDelete(record) {
  message.success(`已删除用户: ${record.nickname || record.username}`)
  doSearch()
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(doSearch)
</script>

<style scoped>
.page-container {
  max-width: 1400px;
}

.search-card {
  margin-bottom: 16px;
  border-radius: 8px;
}

.table-card {
  border-radius: 8px;
}

.no-avatar {
  width: 40px;
  height: 40px;
  background: #fafafa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bfbfbf;
  font-size: 16px;
}

.more-action {
  white-space: nowrap;
}
</style>