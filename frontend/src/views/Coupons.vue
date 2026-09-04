<template>
  <div class="coupons-page">
    <a-card title="优惠券管理" :bordered="false">
      <template #extra>
        <a-space>
          <a-button type="primary" @click="showCreateModal">
            <PlusOutlined /> 新建优惠券
          </a-button>
          <a-button @click="fetchList">
            <ReloadOutlined /> 刷新
          </a-button>
        </a-space>
      </template>

      <a-table :columns="columns" :data-source="list" :loading="loading" :pagination="pagination" row-key="id" @change="handleTableChange">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            <a-tag :color="record.type === 'FULL_REDUCTION' ? 'red' : record.type === 'DISCOUNT' ? 'blue' : 'green'">
              {{ record.type === 'FULL_REDUCTION' ? '满减' : record.type === 'DISCOUNT' ? '折扣' : '现金券' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'value'">
            {{ record.type === 'DISCOUNT' ? `${record.value}折` : `¥${record.value}` }}
          </template>
          <template v-if="column.key === 'minAmount'">
            ¥{{ record.minAmount || 0 }}
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="statusColor(record.status)">{{ statusText(record.status) }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="showEditModal(record)">编辑</a-button>
              <a-popconfirm title="确定删除？" @confirm="handleDelete(record)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal v-model:open="modalVisible" :title="editingItem ? '编辑优惠券' : '新建优惠券'" @ok="handleSave" @cancel="modalVisible = false" width="520px">
      <a-form :model="form" layout="vertical">
        <a-form-item label="优惠券名称" required>
          <a-input v-model:value="form.name" placeholder="例如：满100减20" />
        </a-form-item>
        <a-form-item label="类型" required>
          <a-radio-group v-model:value="form.type">
            <a-radio value="FULL_REDUCTION">满减券</a-radio>
            <a-radio value="DISCOUNT">折扣券</a-radio>
            <a-radio value="CASH">现金券</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item :label="form.type === 'DISCOUNT' ? '折扣' : '优惠金额'" required>
          <a-input-number v-model:value="form.value" :min="0" :max="form.type === 'DISCOUNT' ? 10 : 9999" style="width: 100%" />
        </a-form-item>
        <a-form-item label="最低消费金额">
          <a-input-number v-model:value="form.minAmount" :min="0" style="width: 100%" placeholder="0表示无门槛" />
        </a-form-item>
        <a-form-item label="发放数量" required>
          <a-input-number v-model:value="form.totalCount" :min="1" style="width: 100%" />
        </a-form-item>
        <a-form-item label="有效天数">
          <a-input-number v-model:value="form.validDays" :min="1" style="width: 100%" placeholder="领取后有效天数" />
        </a-form-item>
      </a-form>
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
const editingItem = ref(null)
const form = reactive({ name: '', type: 'FULL_REDUCTION', value: 10, minAmount: 0, totalCount: 100, validDays: 30 })

const pagination = reactive({ current: 1, pageSize: 10, total: 0, showSizeChanger: true, showTotal: (t) => `共 ${t} 条` })

const columns = [
  { title: '名称', dataIndex: 'name' },
  { title: '类型', key: 'type', width: 80 },
  { title: '优惠', key: 'value', width: 100 },
  { title: '最低消费', key: 'minAmount', width: 100 },
  { title: '已发/总量', dataIndex: 'usedCount', width: 100 },
  { title: '状态', key: 'status', width: 80 },
  { title: '创建时间', dataIndex: 'createTime', width: 180 },
  { title: '操作', key: 'action', width: 150 },
]

const statusColor = (s) => { const m = { 0: 'green', 1: 'red' }; return m[s] || 'default' }
const statusText = (s) => { const m = { 0: '进行中', 1: '已结束' }; return m[s] || s }

const fetchList = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/coupons', { params: { page: pagination.current, pageSize: pagination.pageSize } })
    list.value = res.data || []
    pagination.total = res.total || 0
  } catch { list.value = [] } finally { loading.value = false }
}

const handleTableChange = (pag) => { pagination.current = pag.current; pagination.pageSize = pag.pageSize; fetchList() }

const showCreateModal = () => {
  editingItem.value = null
  form.name = ''; form.type = 'FULL_REDUCTION'; form.value = 10; form.minAmount = 0; form.totalCount = 100; form.validDays = 30
  modalVisible.value = true
}

const showEditModal = (record) => {
  editingItem.value = record
  form.name = record.name; form.type = record.type; form.value = record.value; form.minAmount = record.minAmount || 0; form.totalCount = record.totalCount; form.validDays = record.validDays || 30
  modalVisible.value = true
}

const handleSave = async () => {
  if (!form.name) return message.warning('请输入名称')
  try {
    if (editingItem.value) {
      await api.put(`/api/coupons/${editingItem.value.id}`, form)
    } else {
      await api.post('/api/coupons/create', form)
    }
    message.success(editingItem.value ? '更新成功' : '创建成功')
    modalVisible.value = false
    fetchList()
  } catch (e) { message.error(e.response?.data?.detail || '操作失败') }
}

const handleDelete = async (record) => {
  try { await api.delete(`/api/coupons/${record.id}`); message.success('删除成功'); fetchList() }
  catch (e) { message.error(e.response?.data?.detail || '删除失败') }
}

onMounted(fetchList)
</script>