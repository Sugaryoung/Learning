<template>
  <div class="app-container dark">
    <el-container>
      <el-aside width="200px" class="aside">
        <div class="logo">
          <h2>量化交易</h2>
        </div>
        <el-menu
          :default-active="currentRoute"
          class="nav-menu"
          background-color="#1a1a2e"
          text-color="#a0a0b8"
          active-text-color="#409eff"
          router
        >
          <el-menu-item index="/strategies">
            <el-icon><Odometer /></el-icon>
            <span>策略管理</span>
          </el-menu-item>
          <el-menu-item index="/backtest">
            <el-icon><DataLine /></el-icon>
            <span>回测操作</span>
          </el-menu-item>
          <el-menu-item index="/live">
            <el-icon><VideoPlay /></el-icon>
            <span>实盘模拟</span>
          </el-menu-item>
          <el-menu-item index="/data">
            <el-icon><FolderOpened /></el-icon>
            <span>数据管理</span>
          </el-menu-item>
        </el-menu>
        <div class="market-switch">
          <div class="switch-label">市场切换</div>
          <el-switch
            v-model="isCrypto"
            active-text="加密"
            inactive-text="A股"
            @change="handleMarketSwitch"
            style="--el-switch-on-color: #e6a23c"
          />
        </div>
      </el-aside>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const currentRoute = computed(() => route.path)
const isCrypto = ref(false)

const handleMarketSwitch = (val) => {
  if (val) {
    ElMessage.warning('加密货币模式开发中，敬请期待！')
    isCrypto.value = false
  }
}
</script>

<style>
html.dark {
  --el-bg-color: #1a1a2e;
  --el-bg-color-overlay: #16213e;
  --el-text-color-primary: #e0e0e8;
  --el-text-color-regular: #a0a0b8;
  --el-border-color: #2a2a4a;
  --el-fill-color-blank: #16213e;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: #0f0f1a;
  color: #e0e0e8;
}

.app-container {
  height: 100vh;
  overflow: hidden;
}

.aside {
  background-color: #1a1a2e;
  border-right: 1px solid #2a2a4a;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 20px 16px;
  text-align: center;
  border-bottom: 1px solid #2a2a4a;
}

.logo h2 {
  color: #409eff;
  font-size: 20px;
  letter-spacing: 2px;
}

.nav-menu {
  border-right: none;
  flex: 1;
}

.market-switch {
  padding: 16px;
  border-top: 1px solid #2a2a4a;
  text-align: center;
}

.switch-label {
  color: #a0a0b8;
  font-size: 12px;
  margin-bottom: 8px;
}

.main-content {
  background-color: #0f0f1a;
  overflow-y: auto;
  padding: 24px;
}

.el-main {
  --el-main-padding: 24px;
}

:deep(.el-card) {
  background-color: #16213e;
  border-color: #2a2a4a;
  --el-card-text-color: #e0e0e8;
}

:deep(.el-table) {
  --el-table-bg-color: #16213e;
  --el-table-tr-bg-color: #16213e;
  --el-table-header-bg-color: #1a1a2e;
  --el-table-row-hover-bg-color: #1e2a4a;
  --el-table-border-color: #2a2a4a;
  --el-table-text-color: #e0e0e8;
  --el-table-header-text-color: #a0a0b8;
}

:deep(.el-dialog) {
  background-color: #16213e;
  --el-dialog-title-font-size: 16px;
}

:deep(.el-form-item__label) {
  color: #a0a0b8;
}

:deep(.el-input__wrapper) {
  background-color: #1a1a2e;
  box-shadow: 0 0 0 1px #2a2a4a inset;
}

:deep(.el-select__wrapper) {
  background-color: #1a1a2e;
  box-shadow: 0 0 0 1px #2a2a4a inset;
}

:deep(.el-date-editor) {
  --el-date-editor-width: 100%;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: #16213e;
  --el-pagination-text-color: #a0a0b8;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 22px;
  color: #e0e0e8;
  margin-bottom: 4px;
}

.page-header p {
  color: #a0a0b8;
  font-size: 14px;
}
</style>
