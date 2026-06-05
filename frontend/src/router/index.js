import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/strategies' },
  { path: '/strategies', name: 'Strategies', component: () => import('../views/StrategyView.vue') },
  { path: '/backtest', name: 'Backtest', component: () => import('../views/BacktestView.vue') },
  { path: '/live', name: 'Live', component: () => import('../views/LiveView.vue') },
  { path: '/data', name: 'Data', component: () => import('../views/DataView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
