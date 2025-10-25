# 智能家居语音控制系统 - 使用指南

## 快速开始

### 1. 环境准备

确保您的系统满足以下要求：
- Python 3.9+
- 至少 4GB 可用内存（用于 Whisper 模型）
- 网络连接（首次下载 Whisper 模型）

### 2. 安装依赖

```bash
# 安装 uv (如果未安装)
pip install uv

# 克隆项目并安装依赖
cd smart-home-voice-control
uv sync

# 安装开发依赖 (可选)
uv sync --group dev
```

### 3. 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件 (可选)
# 大多数默认配置都可以直接使用
```

### 4. 启动系统

```bash
# 方式 1: 使用启动脚本 (推荐)
python start_server.py

# 方式 2: 直接使用 uv
uv run python -m smart_home.api.main

# 方式 3: 使用 uvicorn
uv run uvicorn smart_home.api.main:app --reload --port 8000
```

### 5. 验证安装

```bash
# 运行测试套件
python run_tests.py

# 运行简单示例
python examples/simple_voice_test.py
```

## 核心功能使用

### 语音控制

#### 通过 API 上传音频文件

```bash
# 使用 curl 上传音频文件
curl -X POST "http://localhost:8000/api/v1/voice/process" \
  -F "audio_file=@your_audio.wav" \
  -F "language=zh"
```

#### 支持的语音指令

**灯光控制：**
- "打开客厅的灯"
- "关闭卧室台灯" 
- "把书房灯调亮一点"
- "将客厅灯光设为红色"
- "关闭所有灯光"

**状态查询：**
- "客厅灯光状态如何"
- "查看所有设备状态"
- "卧室有哪些设备在运行"

**一般对话：**
- "你好"
- "你能做什么"
- "谢谢"

### 设备管理

#### 获取设备列表

```bash
# 获取所有设备
curl http://localhost:8000/api/v1/devices

# 获取特定房间的设备
curl http://localhost:8000/api/v1/devices/room/客厅
```

#### 直接控制设备

```bash
# 打开设备
curl -X POST "http://localhost:8000/api/v1/devices/light_living_room/command" \
  -H "Content-Type: application/json" \
  -d '{"action": "turn_on"}'

# 调节亮度
curl -X POST "http://localhost:8000/api/v1/devices/light_living_room/command" \
  -H "Content-Type: application/json" \
  -d '{"action": "set_brightness", "parameters": {"brightness": 80}}'
```

### Web 界面

访问 http://localhost:8000/docs 使用 Swagger UI 进行交互式 API 测试。

## 开发指南

### 添加新的设备类型

1. **创建设备类**

```python
# src/smart_home/devices/your_device.py
from .base import SmartDevice
from ..core.models import DeviceType, DeviceAction, DeviceCommand, DeviceResponse

class YourDevice(SmartDevice):
    def __init__(self, device_id: str, name: str, room: str, **kwargs):
        super().__init__(device_id, name, DeviceType.YOUR_TYPE, room, **kwargs)
        
    def get_supported_actions(self) -> list[DeviceAction]:
        return [DeviceAction.TURN_ON, DeviceAction.TURN_OFF]
        
    async def execute_command(self, command: DeviceCommand) -> DeviceResponse:
        # 实现设备控制逻辑
        pass
```

2. **注册设备类型**

在 `src/smart_home/core/models.py` 中添加新的设备类型：

```python
class DeviceType(str, Enum):
    # ... 现有类型
    YOUR_TYPE = "your_type"
```

3. **更新 NLU 模型**

在 `src/smart_home/nlu/intent_classifier.py` 中添加识别模式：

```python
def _build_device_patterns(self) -> Dict[str, List[str]]:
    return {
        # ... 现有模式
        "your_type": ["您的设备", "设备别名"],
    }
```

### 扩展语音指令

1. **添加新意图类型**

```python
# src/smart_home/core/models.py
class IntentType(str, Enum):
    # ... 现有意图
    YOUR_INTENT = "your_intent"
```

2. **实现意图处理**

在 `src/smart_home/api/main.py` 中添加处理逻辑：

```python
async def execute_smart_home_command(nlu_result) -> List[DeviceResponse]:
    # ... 现有逻辑
    elif intent.intent == IntentType.YOUR_INTENT:
        responses = await handle_your_intent(entities)
```

### 自定义 NLU 模型

如果需要更高精度的意图识别，可以训练自定义模型：

1. **准备训练数据**

```python
# data/training_data.json
{
    "intents": [
        {
            "intent": "control_light",
            "examples": ["打开灯", "关闭照明", "调节亮度"]
        }
    ]
}
```

2. **训练模型** (可选)

```python
# 使用 transformers 训练自定义分类器
from transformers import AutoTokenizer, AutoModelForSequenceClassification
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEBUG` | `false` | 是否启用调试模式 |
| `API_HOST` | `0.0.0.0` | API 服务器地址 |
| `API_PORT` | `8000` | API 服务器端口 |
| `WHISPER_MODEL` | `base` | Whisper 模型大小 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

### Whisper 模型选择

| 模型 | 大小 | 内存需求 | 速度 | 精度 |
|------|------|----------|------|------|
| `tiny` | 39MB | ~1GB | 最快 | 较低 |
| `base` | 74MB | ~1GB | 快 | 良好 |
| `small` | 244MB | ~2GB | 中等 | 很好 |
| `medium` | 769MB | ~5GB | 慢 | 优秀 |
| `large` | 1550MB | ~10GB | 最慢 | 最佳 |

## 故障排除

### 常见问题

**Q: Whisper 模型下载失败**
```bash
# 手动下载模型
python -c "import whisper; whisper.load_model('base')"
```

**Q: 语音识别效果不好**
- 确保音频质量良好（清晰、无噪音）
- 尝试使用更大的 Whisper 模型
- 检查音频格式和采样率

**Q: API 服务无法启动**
```bash
# 检查端口是否被占用
netstat -an | grep 8000

# 查看详细错误信息
python start_server.py --log-level debug
```

**Q: 设备控制不响应**
- 检查设备是否正确注册
- 验证意图识别结果
- 查看设备日志

### 性能优化

1. **减少模型加载时间**
   - 使用较小的 Whisper 模型
   - 实现模型缓存

2. **提高响应速度**
   - 使用 GPU 加速（如果可用）
   - 优化音频预处理

3. **降低内存使用**
   - 调整批处理大小
   - 定期清理缓存

## 部署指南

### Docker 部署 (计划中)

```dockerfile
FROM python:3.9-slim
# 使用 slim 版本的基础镜像，体积更小，适合生产环境部署
# slim 版本移除了不必要的包和工具，只保留运行 Python 应用所需的最小依赖
COPY . /app
WORKDIR /app
RUN pip install uv && uv sync
EXPOSE 8000
CMD ["python", "start_server.py"]
```

### 生产环境配置

```bash
# 使用环境变量配置
export DEBUG=false
export LOG_LEVEL=WARNING
export SECRET_KEY=your-production-secret-key

# 使用多进程部署
python start_server.py --workers 4 --host 0.0.0.0 --port 8000
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件 