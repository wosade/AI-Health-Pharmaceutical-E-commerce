<template>
  <div class="after-sales-page">
    <a-card title="售后管理" :bordered="false">
      <a-table :columns="columns" :data-source="list" :loading="loading" :pagination="pagination" row-key="id" @change="handleTableChange">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'afterSaleNo'">
            <a @click="showDetail(record)">{{ record.afterSaleNo }}</a>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="statusColor(record.afterSaleStatus)">{{ statusText(record.afterSaleStatus) }}</a-tag>
          </template>
          <template v-if="column.key === 'type'">
            <a-tag>{{ record.afterSaleType === 'REFUND' ? '退款' : '退货退款' }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="showDetail(record)">详情</a-button>
              <a-button v-if="record.afterSaleStatus === 'PENDING'" type="link" size="small" @click="handleApprove(record)">通过</a-button>
              <a-button v-if="record.afterSaleStatus === 'PENDING'" type="link" size="small" danger @click="handleReject(record)">拒绝</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal v-model:open="detailVisible" title="售后详情" width="600px" :footer="null">
      <a-descriptions :column="2" bordered size="small" v-if="detailItem">
        <a-descriptions-item label="售后单号">{{ detailItem.afterSaleNo }}</a-descriptions-item>
        <a-descriptions-item label="订单号">{{ detailItem.orderNo }}</a-descriptions-item>
        <a-descriptions-item label="申请类型">{{ detailItem.afterSaleType === 'REFUND' ? '退款' : '退货退款' }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="statusColor(detailItem.afterSaleStatus)">{{ statusText(detailItem.afterSaleStatus) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="退款金额">¥{{ detailItem.refundAmount }}</a-descriptions-item>
        <a-descriptions-item label="申请原因" :span="2">{{ detailItem.applyReason }}</a-descriptions-item>
        <a-descriptions-item label="申请描述" :span="2">{{ detailItem.applyDescription || '-' }}</a-descriptions-item>
        <a-descriptions-item label="申请时间">{{ detailItem.applyTime }}</a-descriptions-item>
        <a-descriptions-item label="处理时间">{{ detailItem.auditTime || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import api from '../api'

const loading = ref(false)
const list = ref([])
const detailVisible = ref(false)
const detailItem = ref(null)

const pagination = reactive({ current: 1, pageSize: 10, total: 0, showSizeChanger: true, showTotal: (t) => `共 ${t} 条` })

const columns = [
  { title: '售后单号', key: 'afterSaleNo', dataIndex: 'afterSaleNo' },
  { title: '订单号', dataIndex: 'orderNo' },
  { title: '类型', key: 'type', width: 100 },
  { title: '退款金额', dataIndex: 'refundAmount', width: 120 },
  { title: '状态', key: 'status', width: 100 },
  { title: '申请时间', dataIndex: 'applyTime', width: 180 },
  { title: '操作', key: 'action', width: 200 },
]

const statusColor = (s) => {
  const map = { PENDING: 'orange', APPROVED: 'blue', REJECTED: 'red', COMPLETED: 'green' }
  return map[s] || 'default'
}
const statusText = (s) => {
  const map = { PENDING: '待处理', APPROVED: '已通过', REJECTED: '已拒绝', COMPLETED: '已完成' }
  return map[s] || s
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await api.get('/api/after-sales', { params: { page: pagination.current, pageSize: pagination.pageSize } })
    list.value = res.data || []
    pagination.total = res.total || 0
  } catch { list.value = [] } finally { loading.value = false }
}

const handleTableChange = (pag) => { pagination.current = pag.current; pagination.pageSize = pag.pageSize; fetchList() }

const showDetail = (record) => { detailItem.value = record; detailVisible.value = true }

const handleApprove = async (record) => {
  try { await api.put(`/api/after-sales/${record.id}/approve`); message.success('已通过'); fetchList() }
  catch (e) { message.error(e.response?.data?.detail || '操作失败') }
}

const handleReject = async (record) => {
  try { await api.put(`/api/after-sales/${record.id}/reject`); message.success('已拒绝'); fetchList() }
  catch (e) { message.error(e.response?.data?.detail || '操作失败') }
}

onMounted(fetchList)
</script>