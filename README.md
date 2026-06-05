# 量化交易平台 (Quant Trading Platform)

支持 A 股回测与实盘模拟的量化交易系统，架构预留加密货币扩展能力。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.9+ / FastAPI |
| ORM | SQLAlchemy |
| 数据库 | SQLite |
| 数据处理 | pandas / numpy |
| 定时调度 | APScheduler |
| 前端框架 | Vue 3 (Composition API) |
| UI 组件库 | Element Plus (暗色主题) |
| 图表可视化 | ECharts + vue-echarts |
| 构建工具 | Vite 5 |
| HTTP 客户端 | Axios |

## 项目结构

```
Learning/
├── backend/                          # 后端服务
│   ├── main.py                       # FastAPI 入口，CORS / 路由注册 / 启动初始化
│   ├── requirements.txt              # Python 依赖
│   ├── data/                         # 运行时数据目录（SQLite 数据库、CSV 文件）
│   └── app/
│       ├── __init__.py
│       ├── api/                      # REST API 层
│       │   ├── __init__.py           # 聚合所有路由为 api_router
│       │   ├── strategies.py         # 策略管理 CRUD + 内置策略查询 + 源码查看
│       │   ├── backtest.py           # 回测任务提交 / 结果轮询 / 历史记录
│       │   ├── live.py               # 实盘模拟启动 / 停止 / 状态查询
│       │   └── markets.py            # 市场列表 / 股票列表 / CSV 导入
│       ├── backtest/                 # 回测引擎
│       │   ├── __init__.py
│       │   ├── engine.py             # 事件驱动回测引擎（逐 Bar 迭代、交易执行、指标计算）
│       │   └── task_manager.py       # 异步任务管理（threading + task_id 轮询）
│       ├── data/                     # 数据处理层
│       │   ├── __init__.py
│       │   ├── base_handler.py       # BaseDataHandler 抽象基类（可扩展至加密货币）
│       │   └── stock_handler.py      # A 股数据处理器（CSV 加载 / 随机样本生成）
│       ├── live/                     # 实盘模拟
│       │   ├── __init__.py
│       │   └── simulator.py          # LiveSimulator 单例（APScheduler 定时 Tick）
│       ├── models/                   # 数据模型
│       │   ├── __init__.py
│       │   └── database.py           # SQLAlchemy ORM 模型 + 数据库初始化
│       └── strategies/               # 策略模块
│           ├── __init__.py           # STRATEGY_REGISTRY 注册表
│           ├── base.py               # BaseStrategy 抽象基类 / Signal / SignalType
│           ├── sma_cross.py          # SMA 均线交叉策略
│           ├── rsi.py                # RSI 超买超卖策略
│           └── bollinger.py          # 布林带策略
├── frontend/                         # 前端应用
│   ├── index.html                    # Vite 入口 HTML
│   ├── package.json                  # 前端依赖与脚本
│   ├── vite.config.js                # Vite 配置（代理 /api → localhost:8000）
│   ├── dist/                         # 构建产物
│   └── src/
│       ├── main.js                   # Vue 应用入口（注册 Element Plus / Router）
│       ├── App.vue                   # 根组件（侧边栏导航 + 暗色主题 + 市场切换）
│       ├── api/
│       │   ├── index.js              # Axios 实例（baseURL / 超时 / 拦截器）
│       │   └── modules.js            # 全部 API 方法封装
│       ├── router/
│       │   └── index.js              # 路由配置（懒加载）
│       └── views/
│           ├── StrategyView.vue      # 策略管理页
│           ├── BacktestView.vue      # 回测操作页
│           ├── LiveView.vue          # 实盘模拟页
│           └── DataView.vue          # 数据管理页
├── background.md                     # 需求文档
└── README.md
```

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────┐
│                  Frontend (Vue3)                 │
│  ┌──────────┬──────────┬──────────┬───────────┐ │
│  │ 策略管理  │ 回测操作  │ 实盘模拟  │ 数据管理   │ │
│  └────┬─────┴────┬─────┴────┬─────┴─────┬─────┘ │
│       └──────────┴──────────┴───────────┘        │
│                    Axios /api                     │
└───────────────────────┬─────────────────────────┘
                        │  HTTP (Vite Proxy)
┌───────────────────────┴─────────────────────────┐
│               Backend (FastAPI)                   │
│  ┌─────────────────────────────────────────────┐ │
│  │              API Layer (REST)                │ │
│  │  /strategies  /backtest  /live  /markets    │ │
│  └──┬──────────────┬──────────────┬────────────┘ │
│     │              │              │               │
│  ┌──┴───┐   ┌─────┴─────┐  ┌────┴─────┐        │
│  │策略模块│   │ 回测引擎  │  │实盘模拟器│        │
│  │Registry│  │Event-Driven│ │APScheduler│        │
│  └──┬───┘   └─────┬─────┘  └────┬─────┘        │
│     │              │              │               │
│  ┌──┴──────────────┴──────────────┴─────┐        │
│  │          数据处理层 (Data Handler)     │        │
│  │  BaseDataHandler → StockDataHandler   │        │
│  │                    CryptoDataHandler  │        │
│  │                       (预留)          │        │
│  └──────────────────┬───────────────────┘        │
│                     │                             │
│  ┌──────────────────┴───────────────────┐        │
│  │       SQLite (SQLAlchemy ORM)        │        │
│  └──────────────────────────────────────┘        │
└──────────────────────────────────────────────────┘
```

### 策略模块 — 注册表模式

所有策略继承 `BaseStrategy` 抽象基类，实现 `init(data)` 和 `next(bar, portfolio) → Signal` 接口。通过 `STRATEGY_REGISTRY` 字典注册，新增策略只需创建类并注册即可自动出现在前端：

```python
STRATEGY_REGISTRY = {
    "sma_cross": SMACrossStrategy,    # SMA 均线交叉
    "rsi": RSIStrategy,               # RSI 超买超卖
    "bollinger": BollingerBandStrategy, # 布林带
}
```

**内置策略说明：**

| 策略 | 类型标识 | 默认参数 | 买入条件 | 卖出条件 |
|------|---------|----------|---------|---------|
| SMA 均线交叉 | `sma_cross` | `short_period=5, long_period=20` | 短期均线上穿长期均线（金叉） | 短期均线下穿长期均线（死叉） |
| RSI 超买超卖 | `rsi` | `rsi_period=14, oversold=30, overbought=70` | RSI 低于超卖线 | RSI 高于超买线 |
| 布林带 | `bollinger` | `period=20, std_dev=2.0` | 价格跌破下轨 | 价格突破上轨 |

### 数据处理层 — 可扩展设计

```
BaseDataHandler (抽象基类)
├── StockDataHandler     # A 股：CSV 加载 / 随机样本数据生成
└── CryptoDataHandler    # 加密货币：预留扩展接口
```

- `BaseDataHandler` 定义 `fetch_data()` 抽象方法和 `validate_ohlcv()` 静态校验方法
- `StockDataHandler` 支持从 CSV 文件加载历史数据；无 CSV 时自动生成确定性随机样本数据（固定种子），开箱即可体验回测

### 回测引擎 — 事件驱动

回测引擎逐 Bar 迭代 OHLCV 数据，流程如下：

1. 调用 `strategy.init(data)` 初始化指标
2. 遍历每根 Bar，构造 `bar` 和 `portfolio` 上下文
3. 调用 `strategy.next(bar, portfolio)` 获取信号
4. 根据信号执行交易（买入按 100 股整手计算，含滑点和佣金）
5. 记录每日权益曲线和交易记录
6. 计算绩效指标：总收益率、年化收益率、最大回撤、夏普比率、胜率

**异步任务机制：** 回测通过 `BacktestTaskManager` 在守护线程中执行，API 立即返回 `task_id`，前端通过轮询 `/backtest/result/{task_id}` 获取结果。

### 实盘模拟器 — 单例 + APScheduler

`LiveSimulator` 采用线程安全单例模式（`__new__` + `Lock`），使用 APScheduler `BackgroundScheduler` 按固定间隔执行 `_tick()`：

1. 获取最新行情数据
2. 运行策略生成信号
3. 模拟订单执行（含滑点和佣金）
4. 维护持仓、资金、信号和订单记录

## 数据库模型

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `strategy_config` | 用户保存的策略配置 | name, strategy_type, params (JSON) |
| `backtest_record` | 回测记录 | task_id, strategy_type, symbol, 日期范围, 绩效指标, status |
| `trade_log` | 交易日志 | backtest_id, timestamp, action, price, quantity, profit |
| `live_position` | 实盘持仓 | symbol, quantity, avg_cost, current_price |

数据库文件位于 `backend/data/quant.db`，首次启动时自动创建。

## API 接口

所有接口前缀 `/api`，完整文档启动后访问 `http://localhost:8000/docs`（Swagger UI）。

### 策略管理 `/api/strategies`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/strategies/builtin` | 获取内置策略列表（名称、描述、默认参数） |
| GET | `/strategies/code/{type}` | 查看策略源码 |
| GET | `/strategies` | 获取已保存的策略配置列表 |
| POST | `/strategies` | 创建策略配置 |
| PUT | `/strategies/{id}` | 更新策略配置 |
| DELETE | `/strategies/{id}` | 删除策略配置 |

### 回测管理 `/api/backtest`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/backtest/run` | 提交回测任务（异步，返回 task_id） |
| GET | `/backtest/result/{task_id}` | 轮询回测结果 |
| GET | `/backtest/history` | 获取回测历史记录（最近 20 条） |

**回测请求参数：**

```json
{
  "strategy_type": "sma_cross",
  "symbol": "000001.SZ",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_cash": 100000.0,
  "commission_rate": 0.00025,
  "slippage": 0.01,
  "params": { "short_period": 5, "long_period": 20 }
}
```

**回测结果包含：** total_return, annualized_return, max_drawdown, sharpe_ratio, win_rate, final_value, total_trades, trades 列表, equity_curve 权益曲线数据

### 实盘模拟 `/api/live`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/live/start` | 启动实盘模拟 |
| POST | `/live/stop` | 停止实盘模拟 |
| GET | `/live/status` | 获取模拟状态（持仓、盈亏、信号、订单） |

### 市场与数据 `/api/markets`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/markets/supported` | 获取支持的市场列表 |
| GET | `/markets/stocks` | 获取可用股票代码列表 |
| POST | `/markets/import_csv` | 导入 CSV 数据文件 |

## 前端页面

| 页面 | 路由 | 功能说明 |
|------|------|---------|
| 策略管理 | `/strategies` | 内置策略模板展示、策略配置 CRUD、参数动态表单、源码查看 |
| 回测操作 | `/backtest` | 回测参数配置、异步提交、指标卡片（6 项核心指标）、ECharts 权益曲线（含 DataZoom）、交易记录表格（盈亏着色）、CSV 导出 |
| 实盘模拟 | `/live` | 模拟配置（策略/标的/间隔）、启动/停止控制、实时状态卡片（总资产/现金/盈亏/持仓/现价）、信号表、订单表、运行中自动轮询 |
| 数据管理 | `/data` | CSV 文件上传导入、已存储数据列表、支持市场展示 |

**暗色主题：** 全局覆盖 Element Plus CSS 变量，侧边栏导航 + 市场切换（切换至加密货币时显示"开发中"提示）。

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+

### 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务（端口 8000）
python main.py
```

启动后访问 http://localhost:8000/docs 查看 API 文档。

### 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（端口 3000）
npm run dev
```

启动后访问 http://localhost:3000 进入前端界面。

> 前端开发服务器已配置代理，`/api` 请求自动转发至后端 `http://localhost:8000`。

### 构建前端

```bash
cd frontend
npm run build
```

构建产物输出至 `frontend/dist/`，可部署至任意静态服务器。

## 首次交付验证清单

- [x] SMA 回测 API 可调用并返回结果
- [x] 前端展示权益曲线 + 交易记录表格
- [x] 实盘模拟可启动/停止
- [x] 加密货币模式显示"开发中"
- [x] 前端构建通过（`vite build` 无报错）

## 扩展方向

- **加密货币支持：** 实现 `CryptoDataHandler` 继承 `BaseDataHandler`，对接交易所 API 获取实时行情
- **更多策略：** 创建新策略类继承 `BaseStrategy`，在 `STRATEGY_REGISTRY` 中注册即可
- **实盘对接：** 替换 `LiveSimulator` 中的模拟执行为真实交易所下单接口
- **数据源接入：** 对接 Tushare / AKShare 等 A 股数据源，替换随机样本数据
- **用户体系：** 增加用户认证与多账户隔离
- **风控模块：** 增加止损 / 止盈 / 仓位管理规则
