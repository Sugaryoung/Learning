<template>
  <div class="live-page">
    <div class="page-header">
      <h1>实盘模拟</h1>
      <p>启动策略实盘模拟，观察实时信号和持仓变化</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header><span>模拟配置</span></template>
          <el-form :model="form" label-width="100px" label-position="top">
            <el-form-item label="策略类型">
              <el-select v-model="form.strategy_type" style="width: 100%">
                <el-option v-for="s in builtinStrategies" :key="s.type" :label="s.name" :value="s.type" />
              </el-select>
            </el-form-item>
            <el-form-item v-for="(val, key) in form.params" :key="key" :label="'参数: ' + key">
              <el-input-number v-model="form.params[key]" :min="1" :max="200" style="width: 100%" />
            </el-form-item>
            <el-form-item label="股票代码">
              <el-input v-model="form.symbol" placeholder="如 000001.SZ" />
            </el-form-item>
            <el-form-item label="初始资金">
              <el-input-number v-model="form.initial_cash" :min="10000" :step="10000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="轮询间隔(秒)">
              <el-input-number v-model="form.interval_seconds" :min="5" :max="300" style="width: 100%" />
            </el-form-item>
            <el-form-item>
              <el-button
                v-if="!status.running"
                type="primary"
                @click="startLive"
                style="width: 100%"
              >
                <el-icon><VideoPlay /></el-icon> 启动模拟
              </el-button>
              <el-button
                v-else
                type="danger"
                @click="stopLive"
                style="width: 100%"
              >
                <el-icon><VideoPause /></el-icon> 停止模拟
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-row :gutter="12" style="margin-bottom: 16px">
          <el-col :span="4">
            <el-card class="info-card" :body-style="{ padding: '16px' }">
              <div class="info-value" style="color: #409eff">
                <el-icon v-if="status.running"><SuccessFilled /></el-icon>
                <el-icon v-else><CircleCloseFilled /></el-icon>
                {{ status.running ? '运行中' : '未运行' }}
              </div>
              <div class="info-label">状态</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="info-card" :body-style="{ padding: '16px' }">
              <div class="info-value" style="color: #e0e0e8">{{ formatMoney(status.total_value) }}</div>
              <div class="info-label">总资产</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="info-card" :body-style="{ padding: '16px' }">
              <div class="info-value" style="color: #e0e0e8">{{ formatMoney(status.cash) }}</div>
              <div class="info-label">可用资金</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="info-card" :body-style="{ padding: '16px' }">
              <div class="info-value" :style="{ color: status.pnl >= 0 ? '#67c23a' : '#f56c6c' }">
                {{ status.pnl_pct }}%
              </div>
              <div class="info-label">盈亏比例</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="info-card" :body-style="{ padding: '16px' }">
              <div class="info-value" style="color: #e0e0e8">{{ status.position }}</div>
              <div class="info-label">持仓数量</div>
            </el-card>
          </el-col>
          <el-col :span="4">
            <el-card class="info-card" :body-style="{ padding: '16px' }">
              <div class="info-value" style="color: #e6a23c">{{ status.current_price }}</div>
              <div class="info-label">当前价格</div>
            </el-card>
          </el-col>
        </el-row>

        <el-card style="margin-bottom: 16px">
          <template #header><span>实时信号</span></template>
          <el-table :data="status.signals" stripe max-height="200" size="small">
            <el-table-column prop="timestamp" label="时间" width="180" />
            <el-table-column prop="signal_type" label="信号" width="80">
              <template #default="{ row }">
                <el-tag :type="row.signal_type === 'BUY' ? 'danger' : row.signal_type === 'SELL' ? 'success' : 'info'" size="small">
                  {{ row.signal_type === 'BUY' ? '买入' : row.signal_type === 'SELL' ? '卖出' : '持有' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="100" />
            <el-table-column prop="reason" label="原因" />
          </el-table>
        </el-card>

        <el-card>
          <template #header><span>订单记录</span></template>
          <el-table :data="status.orders" stripe max-height="250" size="small">
            <el-table-column prop="timestamp" label="时间" width="180" />
            <el-table-column prop="action" label="方向" width="80">
              <template #default="{ row }">
                <el-tag :type="row.action === 'BUY' ? 'danger' : 'success'" size="small">
                  {{ row.action === 'BUY' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="100" />
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="amount" label="金额" width="120" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag type="success" size="small">已成交</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getBuiltinStrategies, startLive as apiStartLive, stopLive as apiStopLive, getLiveStatus } from '../api/modules'

const builtinStrategies = ref([])
const pollTimer = ref(null)
const form = reactive({
  strategy_type: '',
  symbol: '000001.SZ',
  initial_cash: 100000,
  interval_seconds: 30,
  params: {},
})
const status = reactive({
  running: false,
  symbol: '',
  initial_cash: 100000,
  cash: 0,
  position: 0,
  position_value: 0,
  total_value: 0,
  pnl: 0,
  pnl_pct: 0,
  current_price: 0,
  signals: [],
  orders: [],
})

const formatMoney = (v) => {
  if (!v && v !== 0) return '0.00'
  return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const loadStatus = async () => {
  try {
    const data = await getLiveStatus()
    Object.assign(status, data)
  } catch (e) {
    console.error(e)
  }
}

const startLive = async () => {
  try {
    await apiStartLive({
      strategy_type: form.strategy_type,
      symbol: form.symbol,
      initial_cash: form.initial_cash,
      interval_seconds: form.interval_seconds,
      params: form.params,
    })
    ElMessage.success('实盘模拟已启动')
    loadStatus()
    startPolling()
  } catch (e) {
    ElMessage.error('启动失败')
  }
}

const stopLive = async () => {
  try {
    await apiStopLive()
    ElMessage.success('实盘模拟已停止')
    stopPolling()
    loadStatus()
  } catch (e) {
    ElMessage.error('停止失败')
  }
}

const startPolling = () => {
  stopPolling()
  pollTimer.value = setInterval(loadStatus, 3000)
}

const stopPolling = () => {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

onMounted(async () => {
  try {
    const data = await getBuiltinStrategies()
    builtinStrategies.value = data
    if (data.length > 0) {
      form.strategy_type = data[0].type
      form.params = { ...data[0].default_params }
    }
  } catch (e) {
    console.error(e)
  }
  await loadStatus()
  if (status.running) {
    startPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.info-card {
  text-align: center;
}

.info-value {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #a0a0b8;
}
</style>
