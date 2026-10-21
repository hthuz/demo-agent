# ReAct Agent Demo

一个最小可用的 ReAct Agent 实现，支持"思考 → 工具调用 → 观察 → 继续"的循环。

## 特性

- ✅ 完整的 ReAct 循环实现
- ✅ 支持多种 LLM 模型（OpenAI、DeepSeek）
- ✅ 4 个内置工具（Calculator, FileReader, Directory, FinalAnswer）
- ✅ 实时展示工具调用过程
- ✅ CLI 交互界面
- ✅ 单元测试覆盖

## 架构

```
工具层 (Tools) ← 编排层 (ReAct Agent) → 模型层 (LLM)
```

详细架构见 [CLAUDE.md](CLAUDE.md)

## 安装

```bash
# 使用 uv 安装依赖
uv sync

# 或使用 pip
pip install -e .
```

## 配置

创建 `.env` 文件来配置 Agent：

```bash
# 模型提供商配置（必需）
# 目前仅支持: openai 或 deepseek
MODEL_PROVIDER=deepseek

# API 密钥（根据 MODEL_PROVIDER 选择对应的密钥）
OPENAI_API_KEY=your-openai-api-key      # MODEL_PROVIDER=openai 时必需
DEEPSEEK_API_KEY=your-deepseek-api-key  # MODEL_PROVIDER=deepseek 时必需

# LLM 模型配置
MODEL_NAME=deepseek-flash           # OpenAI: gpt-4, gpt-3.5-turbo 等
                                    # DeepSeek: deepseek-flash, deepseek-v4-pro
TEMPERATURE=0.7                     # 可选: 0.0-2.0，控制输出随机性
MAX_TOKENS=2000                     # 可选: 最大生成 token 数

# Agent 配置
MAX_ITERATIONS=10                   # 可选: 最大循环次数
VERBOSE=true                        # 可选: 是否显示详细输出

# 工具配置
FILE_READER_BASE_PATH=.             # 可选: FileReader 基础路径
FILE_READER_MAX_SIZE=10000          # 可选: 最大文件读取字符数
DIRECTORY_BASE_PATH=.               # 可选: Directory 基础路径
```

**重要说明：**
- `MODEL_PROVIDER` 决定使用哪个 LLM 提供商，目前仅支持 `openai` 和 `deepseek`
- 根据 `MODEL_PROVIDER` 的值，需要设置对应的 API Key
- `MODEL_NAME` 需要与所选提供商兼容

### 配置优先级

1. 显式传递的参数（最高优先级）
2. 环境变量 / .env 文件
3. 默认值（最低优先级）

```python
from agent.config import get_config
from agent.models.openai_model import OpenAIModel

# 使用配置文件中的值
config = get_config()
model = OpenAIModel(config=config)

# 或者覆盖特定配置
model = OpenAIModel(temperature=0.5)  # 覆盖 TEMPERATURE 配置
```

## 使用

### CLI 交互模式

```bash
uv run python -m agent.react.cli
```

### 单次查询

```bash
uv run python -m agent.react.cli --query "计算 25 * 4"
```

### 代码调用

#### 使用 Model Factory（推荐）

```python
from agent.react.agent import ReActAgent
from agent.models.factory import create_model
from agent.config import get_config

config = get_config()

# 根据 MODEL_PROVIDER 配置自动创建对应的模型
model = create_model(config=config)

agent = ReActAgent(model=model, config=config)
result = agent.run("列出当前目录的文件，然后计算文件数量")
print(result)
```

#### 显式使用 OpenAI 模型

```python
from agent.react.agent import ReActAgent
from agent.models.openai_model import OpenAIModel

model = OpenAIModel()
agent = ReActAgent(model=model)

result = agent.run("列出当前目录的文件，然后计算文件数量")
print(result)
```

#### 显式使用 DeepSeek 模型

```python
from agent.react.agent import ReActAgent
from agent.models.deepseek_model import DeepSeekModel

# 使用 deepseek-flash 模型（快速、经济）
model = DeepSeekModel(model="deepseek-flash")
agent = ReActAgent(model=model)

result = agent.run("列出当前目录的文件，然后计算文件数量")
print(result)

# 或使用 deepseek-v4-pro 处理复杂任务
model = DeepSeekModel(model="deepseek-v4-pro")
agent = ReActAgent(model=model)
```

## 可用工具

1. **Calculator** - 数学计算
   - 示例：`计算 (12 + 8) * 3`

2. **FileReader** - 读取文件
   - 示例：`读取 README.md 文件`

3. **Directory** - 列出目录内容
   - 示例：`列出当前目录的所有文件`

4. **FinalAnswer** - 返回最终答案（Agent 自动调用）

## 测试

```bash
# 运行所有测试
uv run pytest

# 运行测试并查看覆盖率
uv run pytest --cov=src/agent --cov-report=html
```

## 示例对话

```
User: 计算 15 * 8，然后告诉我结果是否大于 100

─────────────────────────────────────
🤔 Thought: I need to calculate 15 * 8 first
🔧 Action: Calculator
📝 Input: {"math_expression": "15 * 8"}
⏳ Executing...
📊 Observation: 120
─────────────────────────────────────

🤔 Thought: Now I can compare 120 with 100
🔧 Action: FinalAnswer
📝 Input: {"answer": "15 * 8 = 120，结果大于 100"}
✅ Final Answer: 15 * 8 = 120，结果大于 100
```

## 开发

```bash
# 安装开发依赖
uv sync --extra dev

# 运行测试
uv run pytest

# 代码格式化
uv run black src/ tests/

# 类型检查
uv run mypy src/
```

## License

MIT
