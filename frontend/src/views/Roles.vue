<template>
  <div class="roles-page">
    <a-card title="角色管理" :bordered="false">
      <template #extra>
        <a-space>
          <a-button type="primary" @click="showCreateModal">
            <PlusOutlined /> 新建角色
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
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 1 ? 'green' : 'red'">
              {{ record.status === 1 ? '启用' : '禁用' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="showPermissionModal(record)">权限</a-button>
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
      :title="editingItem ? '编辑角色' : '新建角色'"
      @ok="handleSave"
      @cancel="modalVisible = false"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="角色名称" required>
          <a-input v-model:value="form.name" placeholder="例如：管理员、操作员" />
        </a-form-item>
        <a-form-item label="角色编码" required>
          <a-input v-model:value="form.code" placeholder="例如：admin、operator" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" :rows="3" placeholder="角色描述" />
        </a-form-item>
        <a-form-item label="状态">
          <a-switch v-model:checked="form.status" checked-children="启用" un-checked-children="禁用" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:open="permModalVisible"
      title="分配权限"
      width="600px"
      @ok="handleSavePermissions"
      @cancel="permModalVisible = false"
    >
      <a-tree
        v-model:checkedKeys="selectedPerms"
        :tree-data="permTree"
        checkable
        :default-expand-all="true"
        :replace-fields="{ key: 'id', title: 'name' }"
      />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import api from '../api'

const loading = ref(false)
const list = ref([])
const modalVisible = ref(false)
const permModalVisible = ref(false)
const editingItem = ref(null)
const permRole = ref(null)
const permTree = ref([])
const selectedPerms = ref([])

const form = reactive({ name: '', code: '', description: '', status: true })
const pagination = reactive({ current: 1, pageSize: 10, total: 0, showSizeChanger: true, showTotal: (t) => `共 ${t} 条` })

const columns = [
  { title: '角色名称', dataIndex: 'name' },
  { title: '角色编码', dataIndex: 'code' },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '状态', key: 'status', width: 80 },
  { title: '创建时间', dataIndex: 'createTime', width: 180 },
  { title: '操作', key: 'action', width: 220 },
]

const fetchList = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/roles', { params: { page: pagination.current, pageSize: pagination.pageSize } })
    list.value = res.data || []
    pagination.total = res.total || 0
  } catch { list.value = [] } finally { loading.value = false }
}

const handleTableChange = (pag) => { pagination.current = pag.current; pagination.pageSize = pag.pageSize; fetchList() }

const showCreateModal = () => {
  editingItem.value = null
  form.name = ''; form.code = ''; form.description = ''; form.status = true
  modalVisible.value = true
}

const showEditModal = (record) => {
  editingItem.value = record
  form.name = record.name; form.code = record.code; form.description = record.description || ''; form.status = record.status === 1
  modalVisible.value = true
}

const handleSave = async () => {
  if (!form.name || !form.code) return message.warning('请填写名称和编码')
  try {
    const data = { ...form, status: form.status ? 1 : 0 }
    if (editingItem.value) {
      await api.put(`/api/roles/${editingItem.value.id}`, data)
    } else {
      await api.post('/api/roles/create', data)
    }
    message.success(editingItem.value ? '更新成功' : '创建成功')
    modalVisible.value = false
    fetchList()
  } catch (e) { message.error(e.response?.data?.detail || '操作失败') }
}

const handleDelete = async (record) => {
  try { await api.delete(`/api/roles/${record.id}`); message.success('删除成功'); fetchList() }
  catch (e) { message.error(e.response?.data?.detail || '删除失败') }
}

const showPermissionModal = async (record) => {
  permRole.value = record
  try {
    const [treeRes, permRes] = await Promise.all([
      api.get('/api/permissions/tree'),
      api.get(`/api/roles/${record.id}/permissions`)
    ])
    permTree.value = treeRes.data || []
    selectedPerms.value = (permRes.data || []).map(p => p.id)
  } catch { permTree.value = []; selectedPerms.value = [] }
  permModalVisible.value = true
}

const handleSavePermissions = async () => {
  try {
    await api.put(`/api/roles/${permRole.value.id}/permissions`, { permissionIds: selectedPerms.value })
    message.success('权限分配成功')
    permModalVisible.value = false
  } catch (e) { message.error(e.response?.data?.detail || '操作失败') }
}

onMounted(fetchList)
</script>