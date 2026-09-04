<template>
  <div class="page-container">
    <a-card :bordered="false" class="search-card">
      <a-row :gutter="16" align="middle">
        <a-col :flex="1">
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索药品名称..."
            enter-button="搜索"
            size="middle"
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
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'coverImage'">
            <a-image
              v-if="record.coverImage"
              :src="record.coverImage"
              :width="48"
              :height="48"
              style="object-fit: cover; border-radius: 4px"
              :preview="{ mask: '预览' }"
            />
            <div v-else class="no-image">暂无</div>
          </template>
          <template v-else-if="column.key === 'categoryNames'">
            <a-tag v-for="cat in (record.categoryNames || [])" :key="cat" color="blue" style="margin: 2px">
              {{ cat }}
            </a-tag>
            <span v-if="!record.categoryNames?.length">-</span>
          </template>
          <template v-else-if="column.key === 'tagNames'">
            <a-tag v-for="tag in (record.tagNames || []).slice(0, 4)" :key="tag" color="processing" style="margin: 2px">
              {{ tag }}
            </a-tag>
            <a-tooltip v-if="(record.tagNames || []).length > 4" :title="record.tagNames.slice(4).join('、')">
              <a-tag style="margin: 2px">+{{ record.tagNames.length - 4 }}</a-tag>
            </a-tooltip>
            <span v-if="!record.tagNames?.length">-</span>
          </template>
          <template v-else-if="column.key === 'price'">
            <span class="price-text">¥{{ record.price }}</span>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="record.status === 1 ? 'success' : 'default'">
              {{ record.status === 1 ? '上架' : '下架' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a @click="handleView(record)">详情</a>
              <a @click="handleEdit(record)">编辑</a>
              <a-popconfirm
                title="确定要删除该商品吗？"
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
      title="商品详情"
      :footer="null"
      width="640px"
    >
      <a-descriptions v-if="currentProduct" bordered :column="2" size="small">
        <a-descriptions-item label="商品名称">{{ currentProduct.name }}</a-descriptions-item>
        <a-descriptions-item label="价格">¥{{ currentProduct.price }}</a-descriptions-item>
        <a-descriptions-item label="库存">{{ currentProduct.stock }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="currentProduct.status === 1 ? 'success' : 'default'">
            {{ currentProduct.status === 1 ? '上架' : '下架' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="描述" :span="2">{{ currentProduct.description || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { searchProducts } from '../api/products.js'

const keyword = ref('')
const list = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentProduct = ref(null)

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条`,
})

const columns = [
  { title: '商品封面', key: 'coverImage', width: 90 },
  { title: '商品名称', dataIndex: 'name', ellipsis: true, width: 180 },
  { title: '分类', key: 'categoryNames', width: 160 },
  { title: '标签', key: 'tagNames', width: 200 },
  { title: '价格', key: 'price', width: 100, align: 'right' },
  { title: '库存', dataIndex: 'stock', width: 80, align: 'center' },
  { title: '状态', key: 'status', width: 80, align: 'center' },
  { title: '操作', key: 'action', width: 180, fixed: 'right' },
]

async function doSearch() {
  loading.value = true
  try {
    const res = await searchProducts(keyword.value)
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

function handleView(record) {
  currentProduct.value = record
  detailVisible.value = true
}

function handleEdit(record) {
  message.info(`编辑商品: ${record.name}`)
}

function handleDelete(record) {
  message.success(`已删除商品: ${record.name}`)
  doSearch()
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

.no-image {
  width: 48px;
  height: 48px;
  background: #fafafa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bfbfbf;
  font-size: 12px;
}
</style>