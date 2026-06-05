<template>
  <div class="backtest-page">
    <div class="page-header">
      <h1>回测操作</h1>
      <p>选择策略和参数，运行历史数据回测</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header><span>回测参数</span></template>
          <el-form :model="form" label-width="100px" label-position="top">
            <el-form-item label="策略类型">
              <el-select v-model="form.strategy_type" style="width: 100%" @change="onStrategyChange">
                <el-option v-for="s in builtinStrategies" :key="s.type" :label="s.name" :value="s.type" />
              </el-select>
            </el-form-item>
            <el-form-item v-for="(val, key) in form.params" :key="key" :label="'参数: ' + key">
              <el-input-number v-model="form.params[key]" :min="1" :max="200" style="width: 100%" />
            </el-form-item>
            <el-form-item label="股票代码">
              <el-input v-model="form.symbol" placeholder="如 000001.SZ" />
            </el-form-item>
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="初始资金">
              <el-input-number v-model="form.initial_cash" :min="10000" :step="10000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="手续费率">
              <el-input-number v-model="form.commission_rate" :min="0" :max="0.01" :step="0.00005" :precision="5" style="width: 100%" />
            </el-form-item>
            <el-form-item label="滑点(元)">
              <el-input-number v-model="form.slippage" :min="0" :max="1" :step="0.01" :precision="2" style="width: 100%" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="runBacktest" :loading="running" style="width: 100%">
                {{ running ? '回测运行中...' : '开始回测' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <div v-if="result">
          <el-row :gutter="12" style="margin-bottom: 16px">
            <el-col :span="4" v-for="card in metricCards" :key="card.label">
              <el-card class="metric-card" :body-style="{ padding: '16px' }">
                <div class="metric-value" :style="{ color: card.color }">{{ card.value }}</div>
                <div class="metric-label">{{ card.label }}</div>
              </el-card>
            </el-col>
          </el-row>

          <el-card style="margin-bottom: 16px">
            <template #header><span>资金曲线</span></template>
            <v-chart :option="equityOption" style="height: 350px" autoresize />
          </el-card>

          <el-card>
            <template #header>
              <div class="card-header">
                <span>交易记录</span>
                <el-button size="small" @click="exportCSV">导出CSV</el-button>
              </div>
            </template>
            <el-table :data="result.trades" stripe max-height="300" size="small">
              <el-table-column prop="timestamp" label="时间" width="160" />
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
              <el-table-column prop="commission" label="手续费" width="100" />
              <el-table-column prop="profit" label="盈亏" width="100">
                <template #default="{ row }">
                  <span :style="{ color: row.profit >= 0 ? '#67c23a' : '#f56c6c' }">
                    {{ row.profit >= 0 ? '+' : '' }}{{ row.profit }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <el-card v-else>
          <el-empty description="请配置参数并运行回测" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { getBuiltinStrategies, runBacktest as apiRunBacktest, getBacktestResult } from '../api/modules'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent])

const builtinStrategies = ref([])
const running = ref(false)
const result = ref(null)
const dateRange = ref(['2024-01-01', '2024-12-31'])
const form = reactive({
  strategy_type: '',
  symbol: '000001.SZ',
  initial_cash: 100000,
  commission_rate: 0.00025,
  slippage: 0.01,
  params: {},
})

const metricCards = computed(() => {
  if (!result.value) return []
  const r = result.value
  return [
    { label: '总收益率', value: r.total_return + '%', color: r.total_return >= 0 ? '#67c23a' : '#f56c6c' },
    { label: '年化收益', value: r.annualized_return + '%', color: r.annualized_return >= 0 ? '#67c23a' : '#f56c6c' },
    { label: '最大回撤', value: r.max_drawdown + '%', color: '#f56c6c' },
    { label: '夏普比率', value: r.sharpe_ratio, color: '#409eff' },
    { label: '胜率', value: r.win_rate + '%', color: r.win_rate >= 50 ? '#67c23a' : '#e6a23c' },
    { label: '交易次数', value: r.total_trades, color: '#a0a0b8' },
  ]
})

const equityOption = computed(() => {
  if (!result.value || !result.value.equity_curve) return {}
  const curve = result.value.equity_curve
  const dates = curve.map((r) => r.timestamp?.split(' ')[0] || r.timestamp)
  const values = curve.map((r) => r.total_value)

  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['总资产'], textStyle: { color: '#a0a0b8' } },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: dates, axisLabel: { color: '#a0a0b8', rotate: 30 } },
    yAxis: { type: 'value', axisLabel: { color: '#a0a0b8' }, splitLine: { lineStyle: { color: '#2a2a4a' } } },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }],
    series: [
      {
        name: '总资产',
        type: 'line',
        data: values,
        smooth: true,
        lineStyle: { color: '#409eff', width: 2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64,158,255,0.3)' },
              { offset: 1, color: 'rgba(64,158,255,0.02)' },
            ],
          },
        },
      },
    ],
  }
})

const onStrategyChange = (type) => {
  const s = builtinStrategies.value.find((x) => x.type === type)
  if (s) {
    form.params = { ...s.default_params }
  }
}

const runBacktest = async () => {
  if (!form.strategy_type) {
    ElMessage.warning('请选择策略')
    return
  }
  if (!dateRange.value || dateRange.value.length < 2) {
    ElMessage.warning('请选择时间范围')
    return
  }

  running.value = true
  result.value = null

  try {
    const res = await apiRunBacktest({
      strategy_type: form.strategy_type,
      symbol: form.symbol,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      initial_cash: form.initial_cash,
      commission_rate: form.commission_rate,
      slippage: form.slippage,
      params: form.params,
    })

    const taskId = res.task_id
    pollResult(taskId)
  } catch (e) {
    ElMessage.error('启动回测失败')
    running.value = false
  }
}

const pollResult = async (taskId) => {
  const timer = setInterval(async () => {
    try {
      const res = await getBacktestResult(taskId)
      if (res.status === 'completed') {
        result.value = res.result
        running.value = false
        clearInterval(timer)
        ElMessage.success('回测完成')
      } else if (res.status === 'failed') {
        running.value = false
        clearInterval(timer)
        ElMessage.error('回测失败: ' + (res.result?.error || '未知错误'))
      }
    } catch (e) {
      running.value = false
      clearInterval(timer)
      ElMessage.error('获取结果失败')
    }
  }, 1500)
}

const exportCSV = () => {
  if (!result.value || !result.value.trades) return
  const header = '时间,方向,价格,数量,金额,手续费,盈亏\n'
  const rows = result.value.trades.map(
    (t) => `${t.timestamp},${t.action},${t.price},${t.quantity},${t.amount},${t.commission},${t.profit}`
  )
  const csv = header + rows.join('\n')
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `backtest_${form.symbol}_${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
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
})
</script>

<style scoped>
.metric-card {
  text-align: center;
}

.metric-value {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 12px;
  color: #a0a0b8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
