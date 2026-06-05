<template>
  <div class="data-page">
    <div class="page-header">
      <h1>数据管理</h1>
      <p>管理股票数据，导入CSV文件</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header><span>导入CSV数据</span></template>
          <el-form label-width="100px">
            <el-form-item label="股票代码">
              <el-input v-model="importSymbol" placeholder="如 000001.SZ" />
            </el-form-item>
            <el-form-item label="CSV文件">
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :limit="1"
                accept=".csv"
                :on-change="handleFileChange"
              >
                <el-button type="primary">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">CSV格式，需包含 timestamp, open, high, low, close, volume 列</div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="handleImport" :loading="importing">导入数据</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>已存储数据</span>
              <el-button size="small" @click="loadStocks">刷新</el-button>
            </div>
          </template>
          <el-table :data="stocks" stripe>
            <el-table-column prop="symbol" label="股票代码" />
            <el-table-column prop="name" label="名称" />
          </el-table>

          <el-card style="margin-top: 20px">
            <template #header><span>支持的市场</span></template>
            <el-tag v-for="m in markets" :key="m" style="margin: 4px" size="large">{{ m }}</el-tag>
          </el-card>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listStocks, importCsv, getSupportedMarkets } from '../api/modules'

const importSymbol = ref('')
const uploadRef = ref(null)
const selectedFile = ref(null)
const importing = ref(false)
const stocks = ref([])
const markets = ref([])

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleImport = async () => {
  if (!importSymbol.value) {
    ElMessage.warning('请输入股票代码')
    return
  }
  if (!selectedFile.value) {
    ElMessage.warning('请选择CSV文件')
    return
  }
  importing.value = true
  try {
    await importCsv(importSymbol.value, selectedFile.value)
    ElMessage.success('导入成功')
    loadStocks()
  } catch (e) {
    ElMessage.error('导入失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    importing.value = false
  }
}

const loadStocks = async () => {
  try {
    stocks.value = await listStocks()
  } catch (e) {
    console.error(e)
  }
}

const loadMarkets = async () => {
  try {
    markets.value = await getSupportedMarkets()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadStocks()
  loadMarkets()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
