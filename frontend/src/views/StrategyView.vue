<template>
  <div class="strategy-page">
    <div class="page-header">
      <h1>策略管理</h1>
      <p>管理量化交易策略，查看策略代码和参数配置</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>内置策略模板</span>
              <el-button type="primary" @click="showCreateDialog">
                <el-icon><Plus /></el-icon> 新建策略
              </el-button>
            </div>
          </template>
          <el-table :data="builtinStrategies" stripe>
            <el-table-column prop="type" label="策略类型" width="140" />
            <el-table-column prop="name" label="策略名称" width="160" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="默认参数" width="220">
              <template #default="{ row }">
                <el-tag v-for="(val, key) in row.default_params" :key="key" size="small" style="margin: 2px">
                  {{ key }}={{ val }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="viewCode(row.type)">查看代码</el-button>
                <el-button size="small" type="primary" @click="createFromBuiltin(row)">使用</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>已保存的策略</span>
          </template>
          <el-table :data="savedStrategies" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="name" label="策略名称" width="180" />
            <el-table-column prop="strategy_type" label="类型" width="140" />
            <el-table-column prop="params" label="参数" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="editStrategy(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="codeDialogVisible" :title="codeTitle" width="700px">
      <pre class="code-block">{{ codeContent }}</pre>
    </el-dialog>

    <el-dialog v-model="createDialogVisible" :title="editingStrategy ? '编辑策略' : '新建策略'" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="策略名称">
          <el-input v-model="createForm.name" placeholder="输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="createForm.strategy_type" :disabled="!!editingStrategy" style="width: 100%">
            <el-option v-for="s in builtinStrategies" :key="s.type" :label="s.name" :value="s.type" />
          </el-select>
        </el-form-item>
        <el-form-item v-for="(val, key) in createForm.params" :key="key" :label="'参数: ' + key">
          <el-input-number v-model="createForm.params[key]" :min="1" :max="200" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getBuiltinStrategies,
  getStrategyCode,
  listStrategies,
  createStrategy,
  updateStrategy,
  deleteStrategy,
} from '../api/modules'

const builtinStrategies = ref([])
const savedStrategies = ref([])
const codeDialogVisible = ref(false)
const codeContent = ref('')
const codeTitle = ref('')
const createDialogVisible = ref(false)
const editingStrategy = ref(null)
const createForm = reactive({
  name: '',
  strategy_type: '',
  params: {},
})

const formatDate = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN')
}

const loadBuiltinStrategies = async () => {
  try {
    builtinStrategies.value = await getBuiltinStrategies()
  } catch (e) {
    console.error(e)
  }
}

const loadSavedStrategies = async () => {
  try {
    savedStrategies.value = await listStrategies()
  } catch (e) {
    console.error(e)
  }
}

const viewCode = async (type) => {
  try {
    const res = await getStrategyCode(type)
    codeTitle.value = `${res.name} - 策略代码`
    codeContent.value = res.code
    codeDialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取策略代码失败')
  }
}

const showCreateDialog = () => {
  editingStrategy.value = null
  createForm.name = ''
  createForm.strategy_type = builtinStrategies.value[0]?.type || ''
  createForm.params = { ...(builtinStrategies.value[0]?.default_params || {}) }
  createDialogVisible.value = true
}

const createFromBuiltin = (strategy) => {
  editingStrategy.value = null
  createForm.name = strategy.name
  createForm.strategy_type = strategy.type
  createForm.params = { ...strategy.default_params }
  createDialogVisible.value = true
}

const editStrategy = (row) => {
  editingStrategy.value = row
  createForm.name = row.name
  createForm.strategy_type = row.strategy_type
  try {
    createForm.params = typeof row.params === 'string' ? JSON.parse(row.params) : { ...row.params }
  } catch {
    createForm.params = {}
  }
  createDialogVisible.value = true
}

const handleSave = async () => {
  if (!createForm.name || !createForm.strategy_type) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    if (editingStrategy.value) {
      await updateStrategy(editingStrategy.value.id, {
        name: createForm.name,
        params: createForm.params,
      })
      ElMessage.success('策略已更新')
    } else {
      await createStrategy({
        name: createForm.name,
        strategy_type: createForm.strategy_type,
        params: createForm.params,
      })
      ElMessage.success('策略已创建')
    }
    createDialogVisible.value = false
    loadSavedStrategies()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此策略吗？', '确认', { type: 'warning' })
    await deleteStrategy(id)
    ElMessage.success('策略已删除')
    loadSavedStrategies()
  } catch {
    // cancelled
  }
}

onMounted(() => {
  loadBuiltinStrategies()
  loadSavedStrategies()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.code-block {
  background-color: #0f0f1a;
  color: #a0d8ef;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
  max-height: 500px;
  overflow-y: auto;
}
</style>
