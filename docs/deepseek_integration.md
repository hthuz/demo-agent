# DeepSeek 模型集成文档

## 概述

本次更新为 ReAct Agent 项目添加了 DeepSeek 模型支持，使项目可以灵活选择使用 OpenAI 或 DeepSeek 作为底层 LLM。

**重要限制：目前仅支持 `openai` 和 `deepseek` 两个提供商。**

## 配置方式

通过 `MODEL_PROVIDER` 环境变量来选择使用哪个 LLM 提供商：

```bash
# 在 .env 文件中配置
MODEL_PROVIDER=openai      # 使用 OpenAI（默认）
MODEL_PROVIDER=deepseek    # 使用 DeepSeek
```

系统会根据 `MODEL_PROVIDER` 的值验证对应的 API Key：
- `MODEL_PROVIDER=openai` → 需要 `OPENAI_API_KEY`
- `MODEL_PROVIDER=deepseek` → 需要 `DEEPSEEK_API_KEY`

## 新增文件

### 1. 模型实现
- `src/agent/models/deepseek_model.py` - DeepSeek 模型实现类
  - 继承自 `LLMBase` 抽象基类
  - 兼容 OpenAI API 接口
  - 支持自定义 base_url
  - 默认使用 `deepseek-flash` 模型

### 2. 测试文件
- `tests/test_deepseek_model.py` - DeepSeek 模型完整测试套件
  - 13 个测试用例，覆盖所有功能点
  - 包含初始化、生成、错误处理等场景

### 3. 示例文件
- `examples/demo_deepseek.py` - DeepSeek 使用示例
  - 演示如何初始化和使用 DeepSeek 模型
  - 包含错误处理和配置说明

## 修改文件

### 1. 配置管理 (`src/agent/config.py`)
```python
@property
def deepseek_api_key(self) -> Optional[str]:
    """DeepSeek API key."""
    return os.getenv("DEEPSEEK_API_KEY")
```

### 2. 配置测试 (`tests/test_config.py`)
- 新增 `test_deepseek_api_key_from_env` 测试
- 新增 `test_both_api_keys` 测试
- 更新 `test_config_defaults` 测试

### 3. 文档更新
- `CLAUDE.md` - 更新项目文档，添加 DeepSeek 使用说明
- `README.md` - 更新用户文档，添加 DeepSeek 配置和示例
- `.env.example` - 添加 `DEEPSEEK_API_KEY` 配置项

## 使用方法

### 环境配置

在 `.env` 文件中配置：

```bash
# 选择提供商（必需）
MODEL_PROVIDER=deepseek

# 配置对应的 API Key
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# 配置模型名称
MODEL_NAME=deepseek-flash
```

### 代码示例

#### 方式一：根据配置自动选择（推荐）

```python
from agent.config import get_config
from agent.react.agent import ReActAgent

config = get_config()

# 根据 MODEL_PROVIDER 配置选择模型
if config.model_provider == "openai":
    from agent.models.openai_model import OpenAIModel
    model = OpenAIModel(config=config)
elif config.model_provider == "deepseek":
    from agent.models.deepseek_model import DeepSeekModel
    model = DeepSeekModel(config=config)
else:
    raise ValueError(f"Unsupported provider: {config.model_provider}")

agent = ReActAgent(model=model, config=config)
result = agent.run("计算 15 * 8 的结果")
print(result)
```

#### 方式二：显式指定 DeepSeek 模型

```python
from agent.config import get_config
from agent.models.deepseek_model import DeepSeekModel
from agent.react.agent import ReActAgent

# 初始化配置
config = get_config()

# 创建 DeepSeek 模型实例
model = DeepSeekModel(
    config=config,
    model="deepseek-flash",  # 或 "deepseek-v4-pro" 用于复杂任务
)

# 创建 Agent 并运行
agent = ReActAgent(model=model, config=config)
result = agent.run("计算 15 * 8 的结果")
print(result)
```

### 支持的模型

- `deepseek-flash` - 快速、经济的模型（推荐）
- `deepseek-v4-pro` - 高性能模型，适合复杂任务
- 其他 DeepSeek API 支持的模型名称

## 技术细节

### API 兼容性

DeepSeek API 与 OpenAI API 接口兼容，因此 `DeepSeekModel` 内部使用 OpenAI 的 Python SDK，只需修改 `base_url`：

```python
self.client = OpenAI(
    api_key=self.api_key,
    base_url="https://api.deepseek.com/v1",  # DeepSeek API 端点
)
```

### 配置验证

系统会根据 `MODEL_PROVIDER` 的值验证对应的 API Key：

```python
if self.model_provider == "openai" and not self.openai_api_key:
    errors.append("OPENAI_API_KEY is required when MODEL_PROVIDER is 'openai'")

if self.model_provider == "deepseek" and not self.deepseek_api_key:
    errors.append("DEEPSEEK_API_KEY is required when MODEL_PROVIDER is 'deepseek'")
```

### 错误处理

- API Key 缺失时抛出清晰的 `ValueError` 异常
- API 调用失败时抛出 `RuntimeError` 并包含详细错误信息
- 空响应自动处理为空字符串
- 不支持的 `MODEL_PROVIDER` 会在配置验证时报错

## 测试覆盖

### 测试统计
- **总测试数：83** (从 63 增加到 83)
- **新增测试：20**
  - DeepSeek 模型测试：12 个
  - 配置管理测试：8 个（包含 MODEL_PROVIDER 验证）
- **测试通过率：100%**

### 测试场景
1. 初始化测试
   - 显式 API Key
   - 从配置读取
   - 缺失 API Key
   - 自定义参数

2. 生成测试
   - 成功生成
   - 参数覆盖
   - 空响应处理
   - API 错误处理

3. 配置测试
   - 环境变量读取
   - 多 API Key 共存
   - MODEL_PROVIDER 验证
   - 不同提供商的 API Key 要求

## 设计原则

1. **一致性** - DeepSeekModel 遵循与 OpenAIModel 相同的接口和模式
2. **灵活性** - 支持配置文件、环境变量和显式参数三种配置方式
3. **可测试性** - 完整的单元测试覆盖，使用 mock 避免实际 API 调用
4. **文档完整性** - 更新所有相关文档，提供清晰的使用指南

## 未来扩展

可以按照相同的模式轻松添加其他 LLM 提供商：

1. 创建新的模型类继承 `LLMBase`
2. 在 `config.py` 添加对应的 API Key 属性
3. 编写完整的单元测试
4. 更新文档和示例

## 相关资源

- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- 项目文档：`CLAUDE.md`
- 用户指南：`README.md`
