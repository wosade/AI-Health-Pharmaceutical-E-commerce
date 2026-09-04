<template>
  <div class="page-container">
    <a-card :bordered="false" class="search-card">
      <a-row :gutter="16" align="middle">
        <a-col :flex="1">
          <a-space>
            <a-input
              v-model:value="userId"
              placeholder="输入用户ID..."
              style="width: 180px"
              @press-enter="doSearch"
            />
            <a-select
              v-model:value="statusFilter"
              placeholder="全部状态"
              style="width: 140px"
              allow-clear
              @change="doSearch"
            >
              <a-select-option value="">全部状态</a-select-option>
              <a-select-option value="PENDING_PAYMENT">待支付</a-select-option>
              <a-select-option value="PENDING_SHIPMENT">待发货</a-select-option>
              <a-select-option value="PENDING_RECEIPT">待收货</a-select-option>
              <a-select-option value="COMPLETED">已完成</a-select-option>
              <a-select-option value="REFUNDED">已退款</a-select-option>
              <a-select-option value="AFTER_SALE">售后中</a-select-option>
              <a-select-option value="EXPIRED">已过期</a-select-option>
            </a-select>
          </a-space>
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
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'orderNo'">
            <a style="color: #1890ff; font-family: monospace">{{ record.orderNo }}</a>
          </template>
          <template v-else-if="column.key === 'productInfo'">
            <div v-if="record.productInfo" class="product-cell">
              <a-image
                :src="record.productInfo.productImage"
                :width="50"
                :height="50"
                style="object-fit: cover; border-radius: 4px; flex-shrink: 0"
                :preview="{ mask: '预览' }"
              />
              <div class="product-info">
                <div class="product-name">{{ record.productInfo.productName || '未知商品' }}</div>
                <div class="product-qty">数量: {{ record.productInfo.quantity || 0 }}</div>
              </div>
            </div>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'payType'">
            <a-tag :color="payTypeMap[record.payType]?.color">
              {{ payTypeMap[record.payType]?.text || record.payType || '-' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'orderStatus'">
            <a-tag :color="statusMap[record.orderStatus]?.color">
              {{ statusMap[record.orderStatus]?.text || record.orderStatus }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'totalAmount'">
            <span class="price-text">¥{{ Number(record.totalAmount || record.payAmount || 0).toFixed(2) }}</span>
          </template>
          <template v-else-if="column.key === 'createTime'">
            {{ formatTime(record.createTime) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a @click="handleDetail(record)">详情</a>
              <a v-if="canShip(record.orderStatus)" @click="handleShip(record)">发货</a>
              <a-popconfirm
                v-if="canDelete(record.orderStatus)"
                title="确定要删除该订单吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record)"
              >
                <a style="color: #ff4d4f">删除</a>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:open="detailVisible"
      title="订单详情"
      :footer="null"
      width="640px"
    >
      <a-descriptions v-if="currentOrder" bordered :column="2" size="small">
        <a-descriptions-item label="订单编号">{{ currentOrder.orderNo }}</a-descriptions-item>
        <a-descriptions-item label="订单状态">
          <a-tag :color="statusMap[currentOrder.orderStatus]?.color">
            {{ statusMap[currentOrder.orderStatus]?.text }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="支付方式">
          <a-tag :color="payTypeMap[currentOrder.payType]?.color">
            {{ payTypeMap[currentOrder.payType]?.text }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="订单金额">¥{{ Number(currentOrder.totalAmount || currentOrder.payAmount || 0).toFixed(2) }}</a-descriptions-item>
        <a-descriptions-item label="收货人">{{ currentOrder.receiverName }}</a-descriptions-item>
        <a-descriptions-item label="联系电话">{{ currentOrder.receiverPhone }}</a-descriptions-item>
        <a-descriptions-item label="收货地址" :span="2">{{ currentOrder.receiverAddress || '-' }}</a-descriptions-item>
        <a-descriptions-item label="创建时间" :span="2">{{ formatTime(currentOrder.createTime) }}</a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { getOrdersByUser, getOrdersByStatus } from '../api/orders.js'

const userId = ref('1')
const statusFilter = ref('')
const list = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentOrder = ref(null)

const statusMap = {
  PENDING_PAYMENT: { text: '待支付', color: 'warning' },
  PENDING_SHIPMENT: { text: '待发货', color: 'processing' },
  PENDING_RECEIPT: { text: '待收货', color: 'processing' },
  COMPLETED: { text: '已完成', color: 'success' },
  REFUNDED: { text: '已退款', color: 'error' },
  AFTER_SALE: { text: '售后中', color: 'warning' },
  EXPIRED: { text: '已过期', color: 'error' },
  paid: { text: '已支付', color: 'processing' },
  shipped: { text: '已发货', color: 'processing' },
  completed: { text: '已完成', color: 'success' },
}

const payTypeMap = {
  WALLET: { text: '钱包', color: 'orange' },
  WAIT_PAY: { text: '待支付', color: 'default' },
}

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条`,
})

const columns = [
  { title: '订单编号', key: 'orderNo', width: 180 },
  { title: '商品信息', key: 'productInfo', width: 200 },
  { title: '支付方式', key: 'payType', width: 100 },
  { title: '订单状态', key: 'orderStatus', width: 100 },
  { title: '订单金额', key: 'totalAmount', width: 110, align: 'right' },
  { title: '收货人', dataIndex: 'receiverName', width: 100 },
  { title: '联系电话', dataIndex: 'receiverPhone', width: 130 },
  { title: '创建时间', key: 'createTime', width: 170 },
  { title: '操作', key: 'action', width: 180, fixed: 'right' },
]

function canShip(status) {
  return status === 'PENDING_SHIPMENT' || status === 'paid'
}

function canDelete(status) {
  return status === 'COMPLETED' || status === 'EXPIRED' || status === 'CANCELLED' || status === 'completed'
}

async function doSearch() {
  loading.value = true
  try {
    let res
    if (statusFilter.value) {
      res = await getOrdersByStatus(statusFilter.value)
    } else {
      res = await getOrdersByUser(userId.value)
    }
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
  userId.value = '1'
  statusFilter.value = ''
  doSearch()
}

function handleTableChange(pag) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
}

function handleDetail(record) {
  currentOrder.value = record
  detailVisible.value = true
}

function handleShip(record) {
  message.success(`订单 ${record.orderNo} 已发货`)
  doSearch()
}

function handleDelete(record) {
  message.success(`已删除订单 ${record.orderNo}`)
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

.price-text {
  color: #ff4d4f;
  font-weight: 500;
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-weight: 500;
  color: #262626;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-qty {
  font-size: 12px;
  color: #8c8c8c;
}
</style>