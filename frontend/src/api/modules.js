import api from './index'

export const getBuiltinStrategies = () => api.get('/strategies/builtin')
export const getStrategyCode = (type) => api.get(`/strategies/code/${type}`)
export const listStrategies = () => api.get('/strategies')
export const createStrategy = (data) => api.post('/strategies', data)
export const updateStrategy = (id, data) => api.put(`/strategies/${id}`, data)
export const deleteStrategy = (id) => api.delete(`/strategies/${id}`)

export const runBacktest = (data) => api.post('/backtest/run', data)
export const getBacktestResult = (taskId) => api.get(`/backtest/result/${taskId}`)
export const getBacktestHistory = () => api.get('/backtest/history')

export const startLive = (data) => api.post('/live/start', data)
export const stopLive = () => api.post('/live/stop')
export const getLiveStatus = () => api.get('/live/status')

export const getSupportedMarkets = () => api.get('/markets/supported')
export const listStocks = () => api.get('/markets/stocks')
export const importCsv = (symbol, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/markets/import_csv?symbol=${symbol}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
