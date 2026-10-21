# ReAct Agent 项目文档

## 项目概述

实现一个最小可用的 ReAct Agent，支持"思考 → 工具调用 → 观察 → 继续"的循环。

## 架构设计

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
│   ├── tools/          # 工具层
│   │   ├── base.py     # 工具基类和注册表
│   │   ├── calculator.py
│   │   ├── file_reader.py
│   │   ├── directory.py
│   │   └── final_answer.py  # ⭐ Final Answer 工具
│   ├── models/         # 模型层
│   │   ├── base.py
│   │   └── openai_model.py
│   └── react/          # 编排层
│       ├── agent.py    # ReAct 核心逻辑
│       ├── prompts.py  # Prompt 模板
│       └── cli.py      # CLI 交互界面
├── tests/
│   ├── test_tools.py
│   ├── test_agent.py
│   └── test_integration.py
└── examples/
    └── demo.py
```

## 核心实现方案

### 1. 工具层设计

#### 工具基类 (base.py)

```python
class Tool(ABC):
    """工具抽象基类"""
    name: str          # 工具名称
    description: str   # 工具描述（供 LLM 理解）
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """执行工具，返回结果字符串"""
        pass
    
    def to_dict(self) -> dict:
        """返回工具的 schema 描述"""
        pass
```

#### 必需工具列表

1. **Calculator** - 数学计算
   - 输入：math_expression (字符串)
   - 功能：安全执行数学表达式
   - 示例：`2 + 3 * 4` → `14`

2. **FileReader** - 文件读取
   - 输入：file_path (字符串)
   - 功能：读取文件内容
   - 错误处理：文件不存在、权限问题

3. **Directory** - 目录列表
   - 输入：path (字符串，默认当前目录)
   - 功能：列出目录下的文件和子目录

4. **⭐ FinalAnswer** - 终止循环工具
   - 输入：answer (字符串)
   - 功能：标记 Agent 完成任务，返回最终答案
   - **重要**：这是 Agent 循环的唯一出口

#### 工具注册表

```python
class ToolRegistry:
    """工具注册和管理"""
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Tool:
        return self.tools.get(name)
    
    def get_tools_description(self) -> str:
        """返回所有工具的描述，供 Prompt 使用"""
        pass
```

### 2. 模型层设计

#### LLM 抽象接口

```python
class LLMBase(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成响应"""
        pass
```

#### OpenAI 实现

- 使用 `gpt-4` 或 `gpt-3.5-turbo`
- 支持通过环境变量配置 API Key
- 温度参数：0.7（平衡创造性和准确性）

### 3. ReAct 编排层

#### ReAct 循环流程

```
用户输入
  ↓
构建 System Prompt (包含工具描述和 ReAct 格式说明)
  ↓
┌─→ LLM 生成 (Thought + Action + Action Input)
│    ↓
│  解析输出
│    ↓
│  判断 Action:
│    ├─ FinalAnswer → 返回结果，结束循环 ✅
│    └─ 其他工具 → 执行工具
│         ↓
│       获得 Observation
│         ↓
│       添加到历史 → 回到循环开始 ──┘
│
└─ 最大迭代次数 (10 次) 保护
```

#### Prompt 模板设计

```
You are a helpful assistant with access to tools.

Available Tools:
{tools_description}

⭐ IMPORTANT: When you have the final answer, you MUST use the FinalAnswer tool to return it.

Use the following format:

Thought: [your reasoning about what to do next]
Action: [tool name]
Action Input: [tool input as JSON]
Observation: [tool result will appear here]
... (repeat Thought/Action/Observation as needed)
Thought: I now have the final answer
Action: FinalAnswer
Action Input: {"answer": "your final answer here"}

User Question: {user_input}
```

#### 输出解析

使用正则表达式提取：
- `Thought: (.+)`
- `Action: (.+)`
- `Action Input: (.+)`

#### 状态追踪

```python
class AgentState:
    user_input: str
    history: List[dict]  # 存储每一步的 Thought/Action/Observation
    max_iterations: int = 10
    current_iteration: int = 0
```

### 4. CLI 交互设计

#### 用户体验要求

✅ **实时展示工具调用过程**

```
User: 计算 (12 + 8) * 3，然后读取 README.md 文件

─────────────────────────────────────
🤔 Thought: I need to first calculate the math expression
🔧 Action: Calculator
📝 Input: {"math_expression": "(12 + 8) * 3"}
⏳ Executing...
📊 Observation: 60
─────────────────────────────────────

🤔 Thought: Now I need to read the README.md file
🔧 Action: FileReader
📝 Input: {"file_path": "README.md"}
⏳ Executing...
📊 Observation: [file content...]
─────────────────────────────────────

🤔 Thought: I now have all the information
🔧 Action: FinalAnswer
📝 Input: {"answer": "计算结果是 60。README.md 内容：..."}
✅ Final Answer: 计算结果是 60。README.md 内容：...
─────────────────────────────────────
```

#### CLI 实现要点

1. **颜色输出**：使用 `rich` 库美化输出
2. **实时流式显示**：每一步立即打印，不等整个循环结束
3. **错误提示**：工具调用失败时清晰展示错误信息
4. **循环限制提示**：达到最大迭代次数时警告用户

#### CLI 命令

```bash
# 启动交互式 CLI
uv run python -m agent.react.cli

# 单次查询
uv run python -m agent.react.cli --query "your question"
```

### 5. 测试策略

#### 单元测试 (tests/test_tools.py)

1. **测试计算器工具**
   - 正常数学表达式
   - 除零错误
   - 非法表达式

2. **测试文件读取工具**
   - 读取存在的文件
   - 文件不存在的错误处理
   - 权限错误处理

3. **测试目录列表工具**
   - 列出当前目录
   - 列出空目录
   - 路径不存在的处理

4. **测试 FinalAnswer 工具**
   - 返回正确的答案格式
   - 标记循环结束

#### 集成测试 (tests/test_integration.py)

1. **测试完整 ReAct 循环**
   - 多步工具调用
   - 最终通过 FinalAnswer 结束

2. **测试循环保护机制**
   - 达到最大迭代次数自动停止

3. **测试错误恢复**
   - 工具调用失败后继续运行

## 关键技术决策

### 1. ⭐ FinalAnswer 作为唯一出口

**为什么需要 FinalAnswer 工具？**

- **明确的终止信号**：LLM 必须显式调用 FinalAnswer，避免解析歧义
- **结构化输出**：最终答案有清晰的格式
- **统一流程**：所有操作都通过工具调用，逻辑一致

**替代方案（不采用）**：
- ❌ 通过关键词（如 "Final Answer:"）判断 → 容易误触发
- ❌ 让 LLM 自由输出 → 难以准确解析

### 2. 工具调用可见性

用户必须看到：
- 每一步的思考过程 (Thought)
- 调用了哪个工具 (Action)
- 工具的输入参数 (Action Input)
- 工具的执行结果 (Observation)

这样用户可以：
- 理解 Agent 的决策过程
- 调试问题
- 建立对 Agent 的信任

### 3. 循环保护机制

- **最大迭代次数**：10 次（可配置）
- **超时保护**：单个工具调用最多 30 秒
- **无限循环检测**：如果连续 3 次执行相同的工具调用，发出警告

### 4. 错误处理策略

- 工具执行失败 → 返回错误信息作为 Observation，让 LLM 决定下一步
- LLM 输出解析失败 → 提示 LLM 使用正确格式重试
- 达到最大迭代次数 → 返回当前进度和"无法完成任务"的提示

## 依赖管理

使用 `uv` 管理依赖：

```toml
[project]
dependencies = [
    "openai>=1.0.0",        # OpenAI API
    "pydantic>=2.0.0",      # 数据验证
    "python-dotenv>=1.0.0", # 环境变量
    "rich>=13.0.0",         # CLI 美化输出
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
]
```

## 开发计划

1. ✅ 编写 CLAUDE.md 架构文档
2. ⬜ 实现工具层（包括 FinalAnswer）
3. ⬜ 实现模型层
4. ⬜ 实现 ReAct 编排层
5. ⬜ 实现 CLI 交互
6. ⬜ 编写单元测试
7. ⬜ 编写集成测试
8. ⬜ 完善 README.md

## 使用示例

```python
from agent.react.agent import ReActAgent
from agent.models.openai_model import OpenAIModel

# 初始化
model = OpenAIModel(api_key="your-key")
agent = ReActAgent(model=model)

# 运行查询
result = agent.run("计算 15 * 8 的结果")
print(result)
```

## 注意事项

1. **API Key 安全**：使用 `.env` 文件，不提交到 Git
2. **工具安全性**：Calculator 使用 `ast.literal_eval`，不使用 `eval()`
3. **文件访问限制**：FileReader 只能访问项目目录内的文件
4. **成本控制**：设置最大迭代次数，避免无限循环消耗 API 额度

## 扩展性

未来可以扩展：
- 更多工具（网络搜索、数据库查询等）
- 支持更多 LLM 提供商（Anthropic、本地模型等）
- 持久化对话历史
- 多轮对话能力
- 流式输出
