# ReAct Agent Demo

一个最小可用的 ReAct Agent 实现，支持"思考 → 工具调用 → 观察 → 继续"的循环推理模式。

## 特性

- ✅ 完整的 ReAct 循环实现
- ✅ 支持多种 LLM 模型（OpenAI、DeepSeek）
- ✅ 4 个内置工具（Calculator, FileReader, Directory, FinalAnswer）
- ✅ 实时展示推理和工具调用过程
- ✅ CLI 交互界面
- ✅ 完整的单元测试覆盖（93 个测试）

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      ReAct Agent                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ReAct Loop (思考 → 行动 → 观察)                │  │
│  │  - 解析 LLM 输出                                 │  │
│  │  - 调用工具                                       │  │
│  │  - 收集观察结果                                   │  │
│  │  - 构建下一轮 Prompt                             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────┐          ┌──────────────────────┐   │
│  │  Tool        │          │  LLM Model           │   │
│  │  Registry    │          │  - OpenAI            │   │
│  │              │          │  - DeepSeek          │   │
│  └──────────────┘          └──────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌──────────────────┐          ┌─────────────────┐
│   Built-in Tools │          │   Config System │
│   - Calculator   │          │   - .env file   │
│   - FileReader   │          │   - Env vars    │
│   - Directory    │          │   - Defaults    │
│   - FinalAnswer  │          └─────────────────┘
└──────────────────┘
```

### 核心组件

1. **ReAct Agent** (`src/agent/react/agent.py`)
   - 实现 ReAct 循环逻辑
   - 解析 LLM 响应（Thought, Action, Action Input）
   - 管理对话历史
   - 控制最大迭代次数

2. **Tool Registry** (`src/agent/tools/registry.py`)
   - 工具注册和管理
   - 工具描述生成
   - 工具调用接口

3. **LLM Models** (`src/agent/models/`)
   - 统一的模型抽象接口
   - OpenAI 和 DeepSeek 实现
   - Model Factory 自动路由

4. **Config System** (`src/agent/config.py`)
   - 多层配置管理（.env / 环境变量 / 默认值）
   - 配置验证
   - 优先级处理

## 环境搭建

### 1. 前置要求

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) 包管理器（推荐）或 pip

### 2. 安装依赖

使用 uv（推荐）：
```bash
# 安装基础依赖
uv sync

# 如果需要运行测试，安装开发依赖
uv sync --extra dev
```

或使用 pip：
```bash
# 安装基础依赖
pip install -e .

# 如果需要运行测试，安装开发依赖
pip install -e ".[dev]"
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 模型提供商配置（必需）
# 可选值: openai 或 deepseek
MODEL_PROVIDER=deepseek

# API 密钥配置（根据 MODEL_PROVIDER 选择对应的密钥）
OPENAI_API_KEY=your-openai-api-key      # 使用 OpenAI 时必需
DEEPSEEK_API_KEY=your-deepseek-api-key  # 使用 DeepSeek 时必需

# LLM 模型配置
MODEL_NAME=deepseek-flash           # OpenAI: gpt-4, gpt-3.5-turbo 等
                                    # DeepSeek: deepseek-flash, deepseek-v4-pro
TEMPERATURE=0.7                     # 可选: 0.0-2.0，控制输出随机性
MAX_TOKENS=2000                     # 可选: 最大生成 token 数

# Agent 配置
MAX_ITERATIONS=10                   # 可选: 最大 ReAct 循环次数
VERBOSE=true                        # 可选: 是否显示详细推理过程

# 工具配置
FILE_READER_BASE_PATH=.             # 可选: FileReader 基础路径
FILE_READER_MAX_SIZE=10000          # 可选: 最大文件读取字符数
DIRECTORY_BASE_PATH=.               # 可选: Directory 基础路径
```

**配置说明：**
- `MODEL_PROVIDER` 决定使用哪个 LLM 提供商
- 只需配置对应提供商的 API Key
- `MODEL_NAME` 需要与所选提供商兼容

### 4. 验证安装

确保依赖已正确安装：
```bash
# 使用 uv
uv sync

# 验证 Python 环境
uv run python --version

# 运行测试（可选）
uv run pytest tests/ -v
```

## 如何运行

### CLI 交互模式

启动交互式对话：
```bash
uv run python -m agent.react.cli
```

示例交互：
```
You: 计算 15 * 8 的结果
Agent: 
💭 Thought: 我需要使用计算器工具来计算 15 * 8
🔧 Action: Calculator
📝 Action Input: {"expression": "15 * 8"}
📊 Observation: 120
✅ Final Answer: 120
```

### 单次查询模式

```bash
uv run python -m agent.react.cli --query "计算 25 * 4"
```

### 示例脚本

运行 DeepSeek 演示：
```bash
uv run python examples/demo_deepseek.py
```

运行 OpenAI 演示：
```bash
uv run python examples/demo_openai.py
```

## 内置工具

### 1. Calculator

**功能：** 执行数学表达式计算

**限制：**
- 只支持基本数学运算符：`+`, `-`, `*`, `/`, `**`, `%`, `(`, `)`
- 表达式格式必须严格：不允许字母、下划线等非数字字符
- 会进行安全检查，拒绝潜在危险的表达式
- 除零会返回错误信息

**示例：**
```python
Calculator.execute(expression="15 * 8")  # ✅ 返回 "120"
Calculator.execute(expression="2 ** 10")  # ✅ 返回 "1024"
Calculator.execute(expression="10 / 0")   # ❌ 返回错误信息
Calculator.execute(expression="import os") # ❌ 拒绝执行
```

### 2. FileReader

**功能：** 读取文本文件内容

**限制：**
- 只能读取 `FILE_READER_BASE_PATH` 目录及其子目录内的文件（默认为当前目录 `.`）
- 路径必须是相对路径，会自动拼接到 base_path
- 最大读取字符数受 `FILE_READER_MAX_SIZE` 限制（默认 10000）
- 超过最大长度会被截断并提示
- 不支持读取二进制文件

**示例：**
```python
FileReader.execute(file_path="README.md")      # ✅ 读取当前目录下的 README.md
FileReader.execute(file_path="src/main.py")    # ✅ 读取 src 子目录下的文件
FileReader.execute(file_path="/etc/passwd")    # ❌ 拒绝读取，不在 base_path 内
FileReader.execute(file_path="../secret.txt")  # ❌ 拒绝读取，路径逃逸
```

### 3. Directory

**功能：** 列出目录内容

**限制：**
- 只能列出 `DIRECTORY_BASE_PATH` 目录及其子目录（默认为当前目录 `.`）
- 路径必须是相对路径
- 只显示文件名和类型（文件/目录），不显示详细信息
- 不递归列出子目录内容

**示例：**
```python
Directory.execute(path=".")           # ✅ 列出当前目录
Directory.execute(path="src")         # ✅ 列出 src 子目录
Directory.execute(path="/tmp")        # ❌ 拒绝访问，不在 base_path 内
Directory.execute()                   # ✅ 默认列出当前目录
```

### 4. FinalAnswer

**功能：** 返回最终答案，结束 ReAct 循环

**限制：**
- 必须是 ReAct 循环中的最后一个工具
- 调用后立即结束推理过程
- 答案会保存到对话历史

**示例：**
```python
FinalAnswer.execute(answer="计算结果是 120")  # 返回答案并结束循环
```

## 测试覆盖

项目包含 **93 个测试**，覆盖所有核心功能：

### 1. 配置管理测试 (`tests/test_config.py` - 23 个)
- ✅ 环境变量加载
- ✅ .env 文件解析
- ✅ 默认值处理
- ✅ 配置优先级验证
- ✅ MODEL_PROVIDER 验证
- ✅ 类型转换（bool, int）

### 2. 模型测试 (`tests/test_*_model.py` - 20 个)
- ✅ OpenAI 模型初始化和调用（8 个）
- ✅ DeepSeek 模型初始化和调用（12 个）
- ✅ API 错误处理
- ✅ 参数覆盖
- ✅ 空响应处理

### 3. Model Factory 测试 (`tests/test_factory.py` - 8 个)
- ✅ 根据 MODEL_PROVIDER 自动选择模型
- ✅ 大小写不敏感
- ✅ 不支持的提供商错误处理
- ✅ 缺失 API Key 错误处理
- ✅ 自定义模型名称

### 4. 工具测试 (`tests/test_tools.py` - 29 个)
- ✅ Calculator 各种表达式计算（8 个）
- ✅ FileReader 文件读取和限制（6 个）
- ✅ Directory 目录列出和限制（6 个）
- ✅ FinalAnswer 答案返回（3 个）
- ✅ ToolRegistry 工具注册和管理（6 个）

### 5. Agent 测试 (`tests/test_agent.py` - 15 个)
- ✅ Agent 初始化
- ✅ ReAct 循环执行
- ✅ 工具调用流程
- ✅ 最大迭代次数限制
- ✅ 错误恢复
- ✅ 对话历史管理
- ✅ Prompt 模板生成
- ✅ 响应解析

### 6. 集成测试 (`tests/test_integration.py` - 9 个)
- ✅ 完整计算工作流
- ✅ 多步骤推理
- ✅ 文件读取工作流
- ✅ 工具注册验证
- ✅ 错误处理工作流
- ✅ 端到端场景测试

运行所有测试：
```bash
uv run pytest tests/ -v
```

运行特定测试文件：
```bash
uv run pytest tests/test_agent.py -v
```

查看测试覆盖率：
```bash
uv run pytest tests/ --cov=src/agent --cov-report=html
```

## 项目结构

```
demo-agent/
├── src/agent/              # 源代码
│   ├── config.py           # 配置管理
│   ├── models/             # LLM 模型实现
│   │   ├── base.py         # 模型抽象基类
│   │   ├── openai_model.py # OpenAI 实现
│   │   ├── deepseek_model.py # DeepSeek 实现
│   │   └── factory.py      # 模型工厂
│   ├── tools/              # 工具实现
│   │   ├── base.py         # 工具抽象基类
│   │   ├── calculator.py   # 计算器工具
│   │   ├── file_reader.py  # 文件读取工具
│   │   ├── directory.py    # 目录列出工具
│   │   ├── final_answer.py # 最终答案工具
│   │   └── registry.py     # 工具注册表
│   └── react/              # ReAct Agent 实现
│       ├── agent.py        # Agent 核心逻辑
│       ├── prompt.py       # Prompt 模板
│       └── cli.py          # 命令行接口
├── tests/                  # 测试文件（93 个测试）
├── examples/               # 示例脚本
├── docs/                   # 详细文档
├── .env.example            # 环境变量模板
├── pyproject.toml          # 项目配置
└── README.md               # 本文件
```

## 详细文档

- [CLAUDE.md](CLAUDE.md) - 项目设计和实现细节
- [docs/deepseek_integration.md](docs/deepseek_integration.md) - DeepSeek 集成说明
- [docs/model_factory_summary.md](docs/model_factory_summary.md) - Model Factory 设计文档

## 许可证

MIT License
