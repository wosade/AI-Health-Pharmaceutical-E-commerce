<template>
  <div class="permissions-page">
    <a-card title="权限管理" :bordered="false">
      <template #extra>
        <a-space>
          <a-button type="primary" @click="showCreateModal(null)">
            <PlusOutlined /> 新建权限
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
        :pagination="false"
        row-key="id"
        :default-expand-all-rows="true"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 1 ? 'green' : 'red'">
              {{ record.status === 1 ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="showCreateModal(record)">添加子级</a-button>
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
      :title="editingItem ? '编辑权限' : '新建权限'"
      @ok="handleSave"
      @cancel="modalVisible = false"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="父级权限">
          <a-tree-select
            v-model:value="form.parentId"
            :tree-data="parentTree"
            :field-names="{ key: 'id', title: 'name', children: 'children' }"
            placeholder="无（顶级权限）"
            allow-clear
            tree-default-expand-all
          />
        </a-form-item>
        <a-form-item label="名称" required>
          <a-input v-model:value="form.name" placeholder="权限名称" />
        </a-form-item>
        <a-form-item label="权限编码" required>
          <a-input v-model:value="form.code" placeholder="例如：product:list" />
        </a-form-item>
        <a-form-item label="排序">
          <a-input-number v-model:value="form.sort" :min="0" style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import api from '../api'

const loading = ref(false)
const list = ref([])
const modalVisible = ref(false)
const editingItem = ref(null)
const form = reactive({ parentId: null, name: '', code: '', sort: 0 })

const parentTree = computed(() => {
  const build = (items) => items.map(item => ({
    id: item.id, name: item.name, children: item.children ? build(item.children) : []
  }))
  return build(list.value)
})

const columns = [
  { title: '名称', dataIndex: 'name' },
  { title: '编码', dataIndex: 'code' },
  { title: '排序', dataIndex: 'sort', width: 60 },
  { title: '状态', key: 'status', width: 80 },
  { title: '操作', key: 'action', width: 220 },
]

const fetchList = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/permissions/tree')
    list.value = res.data || []
  } catch { list.value = [] } finally { loading.value = false }
}

const showCreateModal = (parent) => {
  editingItem.value = null
  form.parentId = parent?.id || null
  form.name = ''; form.code = ''; form.sort = 0
  modalVisible.value = true
}

const showEditModal = (record) => {
  editingItem.value = record
  form.parentId = record.parentId || null
  form.name = record.name; form.code = record.code; form.sort = record.sort || 0
  modalVisible.value = true
}

const handleSave = async () => {
  if (!form.name || !form.code) return message.warning('请填写名称和编码')
  try {
    if (editingItem.value) {
      await api.put(`/api/permissions/${editingItem.value.id}`, form)
    } else {
      await api.post('/api/permissions/create', form)
    }
    message.success(editingItem.value ? '更新成功' : '创建成功')
    modalVisible.value = false
    fetchList()
  } catch (e) { message.error(e.response?.data?.detail || '操作失败') }
}

const handleDelete = async (record) => {
  try { await api.delete(`/api/permissions/${record.id}`); message.success('删除成功'); fetchList() }
  catch (e) { message.error(e.response?.data?.detail || '删除失败') }
}

onMounted(fetchList)
</script>