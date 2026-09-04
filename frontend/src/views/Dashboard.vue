<template>
  <div class="dashboard">
    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6" v-for="card in statCards" :key="card.label">
        <a-card hoverable class="stat-card">
          <div class="stat-card-inner">
            <div class="stat-icon" :style="{ background: card.color + '15', color: card.color }">
              <component :is="card.icon" />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="14">
        <a-card title="月度销售额趋势" class="chart-card">
          <div ref="salesChartRef" class="chart-box"></div>
        </a-card>
      </a-col>
      <a-col :span="10">
        <a-card title="订单状态分布" class="chart-card">
          <div ref="statusChartRef" class="chart-box"></div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="近7日订单量" class="chart-card">
          <div ref="dailyChartRef" class="chart-box"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="商品分类分布" class="chart-card">
          <div ref="categoryChartRef" class="chart-box"></div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  UserOutlined,
  OrderedListOutlined,
  MedicineBoxOutlined,
  DollarOutlined,
} from '@ant-design/icons-vue'
import { analyticsSummary, analyticsCharts } from '../api/agent.js'
import * as echarts from 'echarts'

const summary = ref({
  userCount: 0,
  orderCount: 0,
  productCount: 0,
  todaySales: 0,
})

const chartData = ref({
  salesTrend: [],
  orderStatus: [],
  dailyOrders: [],
  categoryDistribution: [],
})

const statCards = computed(() => [
  { icon: UserOutlined, label: '用户总数', value: summary.value.userCount, color: '#1890ff' },
  { icon: OrderedListOutlined, label: '订单总数', value: summary.value.orderCount, color: '#722ed1' },
  { icon: MedicineBoxOutlined, label: '商品数量', value: summary.value.productCount, color: '#52c41a' },
  { icon: DollarOutlined, label: '今日交易额', value: `¥${summary.value.todaySales || 0}`, color: '#fa8c16' },
])

const salesChartRef = ref(null)
const statusChartRef = ref(null)
const dailyChartRef = ref(null)
const categoryChartRef = ref(null)

let charts = []

function initSalesChart() {
  if (!salesChartRef.value) return
  const chart = echarts.init(salesChartRef.value)
  const months = chartData.value.salesTrend.map((d) => d.month)
  const amounts = chartData.value.salesTrend.map((d) => d.amount)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: months, axisLabel: { rotate: 45, fontSize: 11 } },
    yAxis: { type: 'value', name: '元' },
    series: [{
      name: '销售额', type: 'line', data: amounts, smooth: true,
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(24,144,255,0.3)' },
        { offset: 1, color: 'rgba(24,144,255,0.05)' },
      ])},
      lineStyle: { color: '#1890ff', width: 2 },
      itemStyle: { color: '#1890ff' },
    }],
  })
  charts.push(chart)
}

function initStatusChart() {
  if (!statusChartRef.value) return
  const chart = echarts.init(statusChartRef.value)
  const statusMap = {
    PENDING_PAYMENT: '待付款', pending_payment: '待付款',
    PENDING_SHIPMENT: '待发货', pending_shipment: '待发货',
    SHIPPED: '已发货', shipped: '已发货',
    COMPLETED: '已完成', completed: '已完成',
    CANCELLED: '已取消', cancelled: '已取消',
    AFTER_SALE: '售后中', after_sale: '售后中',
    PENDING_RECEIPT: '待收货', pending_receipt: '待收货',
    PAID: '已支付', paid: '已支付',
    REFUNDED: '已退款', refunded: '已退款',
  }
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 11 } },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
      data: chartData.value.orderStatus.map((d) => ({
        name: statusMap[d.name] || d.name, value: d.value,
      })),
      label: { formatter: '{b}\n{d}%' },
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } },
    }],
  })
  charts.push(chart)
}

function initDailyChart() {
  if (!dailyChartRef.value) return
  const chart = echarts.init(dailyChartRef.value)
  const dates = chartData.value.dailyOrders.map((d) => d.date)
  const counts = chartData.value.dailyOrders.map((d) => d.count)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value', name: '单' },
    series: [{
      name: '订单量', type: 'bar', data: counts,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#722ed1' }, { offset: 1, color: '#b37feb' },
        ]),
        borderRadius: [4, 4, 0, 0],
      },
      barWidth: '50%',
    }],
  })
  charts.push(chart)
}

function initCategoryChart() {
  if (!categoryChartRef.value) return
  const chart = echarts.init(categoryChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}' },
    grid: { left: 100, right: 20, top: 10, bottom: 20 },
    xAxis: { type: 'value', name: '商品数' },
    yAxis: {
      type: 'category',
      data: chartData.value.categoryDistribution.map((d) => d.name),
      axisLabel: { fontSize: 11 },
      inverse: true,
    },
    series: [{
      type: 'bar', data: chartData.value.categoryDistribution.map((d) => d.value),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#52c41a' }, { offset: 1, color: '#95de64' },
        ]),
        borderRadius: [0, 4, 4, 0],
      },
      barWidth: '50%',
    }],
  })
  charts.push(chart)
}

function initAllCharts() {
  charts.forEach((c) => c.dispose())
  charts = []
  nextTick(() => {
    initSalesChart()
    initStatusChart()
    initDailyChart()
    initCategoryChart()
  })
}

function handleResize() {
  charts.forEach((c) => c.resize())
}

onMounted(async () => {
  try {
    const [sumRes, chartRes] = await Promise.all([analyticsSummary(), analyticsCharts()])
    if (sumRes.code === 200) summary.value = sumRes.data
    if (chartRes.code === 200) chartData.value = chartRes.data
    initAllCharts()
  } catch (e) {
    console.error('获取数据失败', e)
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach((c) => c.dispose())
})
</script>

<style scoped>
.dashboard { max-width: 1400px; }

.stat-card { border-radius: 8px; }
.stat-card-inner { display: flex; align-items: center; gap: 16px; }
.stat-icon {
  width: 48px; height: 48px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; flex-shrink: 0;
}
.stat-value { font-size: 24px; font-weight: 600; color: rgba(0,0,0,0.85); line-height: 1.2; }
.stat-label { font-size: 13px; color: rgba(0,0,0,0.45); margin-top: 2px; }

.chart-card { border-radius: 8px; }
.chart-box { width: 100%; height: 320px; }
</style>