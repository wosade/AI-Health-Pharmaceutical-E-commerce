<template>
  <div class="knowledge-docs-page">
    <a-page-header :title="knowledgeName" @back="() => $router.push({ name: 'KnowledgeBase' })">
      <template #extra>
        <a-space>
          <a-upload
            :before-upload="handleUpload"
            :show-upload-list="false"
            accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx"
            multiple
          >
            <a-button type="primary">
              <UploadOutlined /> 上传文件
            </a-button>
          </a-upload>
          <a-button @click="fetchList">
            <ReloadOutlined /> 刷新
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <a-card :bordered="false" style="margin-top: 16px">
      <a-upload-dragger
        :before-upload="handleUpload"
        :show-upload-list="false"
        accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx"
        multiple
        style="margin-bottom: 24px; padding: 24px"
      >
        <p class="ant-upload-drag-icon">
          <InboxOutlined style="font-size: 48px; color: #1890ff" />
        </p>
        <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p class="ant-upload-hint">
          支持 PDF、Word、TXT、Markdown、CSV、Excel 格式，可批量上传
        </p>
      </a-upload-dragger>
    </a-card>

    <a-card title="文档列表" :bordered="false" style="margin-top: 16px">
      <a-table
        :columns="columns"
        :data-source="list"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'fileName'">
            <span style="display: flex; align-items: center; gap: 8px">
              <FileTextOutlined style="color: #1890ff" />
              {{ record.fileName }}
            </span>
          </template>
          <template v-if="column.key === 'fileSize'">
            {{ formatSize(record.fileSize) }}
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="statusColor(record.status)">
              {{ statusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'chunkCount'">
            <a-tag color="blue">{{ record.chunkCount || 0 }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleReParse(record)">重新解析</a-button>
              <a-popconfirm title="确定删除？" @confirm="handleDelete(record)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { UploadOutlined, ReloadOutlined, InboxOutlined, FileTextOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import api from '../api'

const route = useRoute()
const kbId = computed(() => route.params.id)
const knowledgeName = computed(() => route.query.name || '知识库文档')

const loading = ref(false)
const list = ref([])
const uploading = ref(false)

const pagination = reactive({ current: 1, pageSize: 10, total: 0, showSizeChanger: true, showTotal: (t) => `共 ${t} 条` })

const columns = [
  { title: '文件名', key: 'fileName', dataIndex: 'fileName' },
  { title: '文件大小', key: 'fileSize', width: 120 },
  { title: '文件类型', dataIndex: 'fileType', width: 100 },
  { title: '状态', key: 'status', width: 100 },
  { title: '分块数', key: 'chunkCount', width: 80 },
  { title: '上传时间', dataIndex: 'createTime', width: 180 },
  { title: '操作', key: 'action', width: 180 },
]

const statusColor = (s) => {
  const map = { PENDING: 'orange', PROCESSING: 'processing', COMPLETED: 'green', FAILED: 'red' }
  return map[s] || 'default'
}
const statusText = (s) => {
  const map = { PENDING: '待处理', PROCESSING: '解析中', COMPLETED: '已完成', FAILED: '失败' }
  return map[s] || s
}

const formatSize = (bytes) => {
  if (!bytes) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) { bytes /= 1024; i++ }
  return `${bytes.toFixed(1)} ${units[i]}`
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await api.get(`/api/knowledge-base/${kbId.value}/documents`, {
      params: { page: pagination.current, pageSize: pagination.pageSize }
    })
    list.value = res.data || []
    pagination.total = res.total || 0
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchList()
}

const handleUpload = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('knowledgeBaseId', kbId.value)
  uploading.value = true
  try {
    await api.post('/api/knowledge-base/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    message.success(`${file.name} 上传成功`)
    fetchList()
  } catch (e) {
    message.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
  return false
}

const handleReParse = async (record) => {
  try {
    await api.post(`/api/knowledge-base/${kbId.value}/documents/${record.id}/reparse`)
    message.success('已开始重新解析')
    fetchList()
  } catch (e) {
    message.error(e.response?.data?.detail || '操作失败')
  }
}

const handleDelete = async (record) => {
  try {
    await api.delete(`/api/knowledge-base/${kbId.value}/documents/${record.id}`)
    message.success('删除成功')
    fetchList()
  } catch (e) {
    message.error(e.response?.data?.detail || '删除失败')
  }
}

onMounted(fetchList)
</script>

<style scoped>
.knowledge-docs-page { padding: 0; }
</style>