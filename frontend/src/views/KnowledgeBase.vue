<template>
  <div class="knowledge-page">
    <a-card title="知识库管理" :bordered="false">
      <template #extra>
        <a-space>
          <a-button type="primary" @click="showCreateModal">
            <PlusOutlined /> 新建知识库
          </a-button>
          <a-button @click="fetchList">
            <ReloadOutlined /> 刷新
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data-source="list"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a @click="goToDocuments(record)">{{ record.name }}</a>
          </template>
          <template v-if="column.key === 'docCount'">
            <a-tag color="blue">{{ record.docCount || 0 }}</a-tag>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 1 ? 'green' : 'red'">
              {{ record.status === 1 ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="goToDocuments(record)">文档</a-button>
              <a-button type="link" size="small" @click="showEditModal(record)">编辑</a-button>
              <a-popconfirm title="确定删除？" @confirm="handleDelete(record)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:open="modalVisible"
      :title="editingItem ? '编辑知识库' : '新建知识库'"
      @ok="handleSave"
      @cancel="modalVisible = false"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="名称" required>
          <a-input v-model:value="form.name" placeholder="知识库名称" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" :rows="3" placeholder="知识库描述" />
        </a-form-item>
        <a-form-item label="向量模型">
          <a-select v-model:value="form.embeddingModel" placeholder="选择向量模型">
            <a-select-option value="text-embedding-ada-002">text-embedding-ada-002</a-select-option>
            <a-select-option value="bge-large-zh">bge-large-zh</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const list = ref([])
const modalVisible = ref(false)
const editingItem = ref(null)
const form = reactive({ name: '', description: '', embeddingModel: 'text-embedding-ada-002' })

const pagination = reactive({ current: 1, pageSize: 10, total: 0, showSizeChanger: true, showTotal: (t) => `共 ${t} 条` })

const columns = [
  { title: '名称', key: 'name', dataIndex: 'name' },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '文档数', key: 'docCount', width: 100 },
  { title: '向量模型', dataIndex: 'embeddingModel', width: 180 },
  { title: '状态', key: 'status', width: 80 },
  { title: '创建时间', dataIndex: 'createTime', width: 180 },
  { title: '操作', key: 'action', width: 200 },
]

const fetchList = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/knowledge-base/list', {
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

const showCreateModal = () => {
  editingItem.value = null
  form.name = ''
  form.description = ''
  form.embeddingModel = 'text-embedding-ada-002'
  modalVisible.value = true
}

const showEditModal = (record) => {
  editingItem.value = record
  form.name = record.name
  form.description = record.description || ''
  form.embeddingModel = record.embeddingModel || 'text-embedding-ada-002'
  modalVisible.value = true
}

const handleSave = async () => {
  if (!form.name.trim()) return message.warning('请输入名称')
  try {
    if (editingItem.value) {
      await api.put(`/api/knowledge-base/${editingItem.value.id}`, form)
    } else {
      await api.post('/api/knowledge-base/create', form)
    }
    message.success(editingItem.value ? '更新成功' : '创建成功')
    modalVisible.value = false
    fetchList()
  } catch (e) {
    message.error(e.response?.data?.detail || '操作失败')
  }
}

const handleDelete = async (record) => {
  try {
    await api.delete(`/api/knowledge-base/${record.id}`)
    message.success('删除成功')
    fetchList()
  } catch (e) {
    message.error(e.response?.data?.detail || '删除失败')
  }
}

const goToDocuments = (record) => {
  router.push({ name: 'KnowledgeDocuments', params: { id: record.id }, query: { name: record.name } })
}

onMounted(fetchList)
</script>

<style scoped>
.knowledge-page { padding: 0; }
</style>