# ReAct Agent 项目文档

## 项目简介

一个最小可用的 ReAct Agent 实现，支持"思考 → 工具调用 → 观察 → 继续"的循环。

**核心功能：**
- 4 个内置工具：Calculator、FileReader、Directory、FinalAnswer
- 支持多步推理和工具调用链
- CLI 交互界面，实时展示推理过程
- 配置管理：通过 `.env` 文件统一配置

## 项目架构

### 三层架构

```
┌─────────────────────────────────────────────────┐
│           编排层 (Orchestration)                 │
│  - ReAct 循环逻辑                                │
│  - 工具调用解析和执行                             │
│  - 状态管理和停止条件                             │
└──────────────┬──────────────────────────────────┘
               │
        ┌──────┴───────┐
        │              │
┌───────▼─────┐  ┌────▼──────┐
│   模型层     │  │  工具层    │
│             │  │           │
│ - LLM 抽象  │  │ - 工具注册 │
│ - Prompt   │  │ - 工具执行 │
└────────────┘  └───────────┘
```

### 目录结构

```
demo-agent/
├── src/agent/
│   ├── config.py           # 配置管理
│   ├── tools/              # 工具层
│   │   ├── base.py
│   │   ├── calculator.py
│   │   ├── file_reader.py
│   │   ├── directory.py
│   │   └── final_answer.py
│   ├── models/             # 模型层
│   │   ├── base.py
│   │   ├── openai_model.py
│   │   └── deepseek_model.py
│   └── react/              # 编排层
│       ├── agent.py
│       ├── prompts.py
│       └── cli.py
├── tests/
│   ├── test_config.py
│   ├── test_tools.py
│   ├── test_agent.py
│   └── test_integration.py
└── examples/
    └── demo.py
```

## 开发规范

### 1. Git 提交规则

**重要：所有 git commit 和 push 操作由用户手动执行，coding agent 不执行 git 提交。**

提交信息格式：
```
<type>: <subject>

<body>

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

类型：`feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

### 2. 测试规范

**每次代码改动后必须：**

1. **补充或更新相关测试**
   - 新增功能 → 添加测试用例
   - 修复 bug → 添加回归测试
   - 重构代码 → 确保测试通过

2. **运行对应的测试**
   ```bash
   # 运行所有测试
   uv run pytest tests/ -v
   
   # 运行特定测试文件
   uv run pytest tests/test_config.py -v
   
   # 运行特定测试类或方法
   uv run pytest tests/test_tools.py::TestCalculator -v
   ```

3. **确保测试通过后再提交代码**

### 3. 配置管理

所有配置通过 `config.py` 集中管理：

**可配置项：**
- `MODEL_PROVIDER` - LLM 提供商（默认：openai）
  - **目前仅支持：`openai` 或 `deepseek`**
- `OPENAI_API_KEY` - OpenAI API 密钥（使用 OpenAI 时必需）
- `DEEPSEEK_API_KEY` - DeepSeek API 密钥（使用 DeepSeek 时必需）
- `MODEL_NAME` - 模型名称
  - OpenAI: gpt-4, gpt-3.5-turbo, gpt-4-turbo 等
  - DeepSeek: deepseek-chat, deepseek-coder 等
- `TEMPERATURE` - 温度参数（默认：0.7）
- `MAX_TOKENS` - 最大 token 数（默认：2000）
- `MAX_ITERATIONS` - 最大循环次数（默认：10）
- `VERBOSE` - 详细输出（默认：true）
- `FILE_READER_BASE_PATH` - 文件读取基础路径（默认：.）
- `FILE_READER_MAX_SIZE` - 文件最大读取字符数（默认：10000）
- `DIRECTORY_BASE_PATH` - 目录列表基础路径（默认：.）

**配置优先级：** 显式参数 > 环境变量 > 默认值

**重要提示：** 
- 根据 `MODEL_PROVIDER` 的值，系统会自动选择对应的模型类
- 设置 `MODEL_PROVIDER=openai` 时，需要配置 `OPENAI_API_KEY`
- 设置 `MODEL_PROVIDER=deepseek` 时，需要配置 `DEEPSEEK_API_KEY`

### 4. 核心实现要点

#### FinalAnswer 工具
- **作用：** ReAct 循环的唯一出口
- **重要性：** LLM 必须调用此工具才能返回最终答案
- **格式：** `{"answer": "最终答案内容"}`

#### 循环保护
- 最大迭代次数：10 次（可配置）
- 防止无限循环和过度消耗 API

#### 安全性
- Calculator 使用 `ast.literal_eval`，不使用 `eval()`
- FileReader 和 Directory 限制在基础路径内访问

## 使用示例

### 方式一：使用 Model Factory（推荐）

通过 `create_model()` 函数，根据 `MODEL_PROVIDER` 配置自动创建对应的模型：

```python
from agent.config import get_config
from agent.models.factory import create_model
from agent.react.agent import ReActAgent

# 加载配置
config = get_config()

# 根据 MODEL_PROVIDER 自动创建模型
model = create_model(config=config)

# 创建 Agent
agent = ReActAgent(model=model, config=config)
result = agent.run("计算 15 * 8 的结果")
print(result)
```

### 方式二：显式指定模型类

#### 使用 OpenAI 模型

```python
from agent.config import get_config
from agent.models.openai_model import OpenAIModel
from agent.react.agent import ReActAgent

# 加载配置
config = get_config()

# 初始化模型和 Agent
model = OpenAIModel(config=config)
agent = ReActAgent(model=model, config=config)

# 运行查询
result = agent.run("计算 15 * 8 的结果")
print(result)
```

#### 使用 DeepSeek 模型

```python
from agent.config import get_config
from agent.models.deepseek_model import DeepSeekModel
from agent.react.agent import ReActAgent

# 加载配置
config = get_config()

# 初始化 DeepSeek 模型
model = DeepSeekModel(
    config=config,
    model="deepseek-chat",  # 或使用 "deepseek-coder" 处理编程任务
)
agent = ReActAgent(model=model, config=config)

# 运行查询
result = agent.run("计算 15 * 8 的结果")
print(result)
```

# 运行查询
result = agent.run("计算 15 * 8 的结果")
print(result)
```

## 测试覆盖

当前测试状态：**90 个测试全部通过**

- `test_config.py` - 23 个配置管理测试（包含 MODEL_PROVIDER 验证）
- `test_factory.py` - 8 个 Model Factory 测试
- `test_deepseek_model.py` - 12 个 DeepSeek 模型测试
- `test_tools.py` - 29 个工具测试
- `test_agent.py` - 12 个 Agent 测试
- `test_integration.py` - 9 个集成测试
