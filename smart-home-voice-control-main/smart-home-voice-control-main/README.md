# 智能家居语音控制系统

一个基于语音识别和自然语言理解的智能家居控制系统，用户可以通过语音指令控制家中的各种智能设备。

## 功能特性

### 🎤 语音识别 (ASR)
- 基于 OpenAI Whisper 的高精度语音转文字
- 支持实时语音识别
- 多语言支持（中文/英文）
- 噪音过滤和音频预处理

### 🧠 意图理解 (NLU)
- 智能意图识别和实体提取
- 支持复杂的家居控制指令
- 上下文理解和多轮对话
- 模糊指令的智能推理

### 🏠 设备控制
- **灯光控制**：开关、亮度调节、颜色变化
- **温度控制**：空调、暖气、温度设定
- **音响控制**：播放音乐、音量调节、切换歌曲
- **窗帘控制**：开关窗帘、调节开合度
- **安防系统**：布防/撤防、门锁控制

### 🌐 API接口
- RESTful API 设计
- WebSocket 实时通信
- MQTT 设备通信协议
- 统一的设备管理接口

## 项目架构

```
smart-home-voice-control/
├── src/smart_home/          # 主要源代码
│   ├── asr/                 # 语音识别模块
│   ├── nlu/                 # 自然语言理解
│   ├── devices/             # 设备控制模块
│   ├── api/                 # API接口
│   └── core/                # 核心功能
├── tests/                   # 测试代码
├── config/                  # 配置文件
├── docs/                    # 文档
└── examples/                # 示例代码
```

## 快速开始

### 1. 环境要求
- Python 3.9+
- uv (Python 包管理器)

### 2. 安装依赖
```bash
# 安装 uv (如果未安装)
pip install uv

# 安装项目依赖
uv sync

# 安装开发依赖
uv sync --group dev
```

### 3. 启动服务
```bash
# 启动 API 服务器
uv run python -m smart_home.api.main

# 或使用 uvicorn
uv run uvicorn smart_home.api.main:app --reload --port 8000
```

## 支持的语音指令示例

### 灯光控制
- "打开客厅的灯"
- "把卧室灯调亮一点"
- "将书房灯光设为暖色调"
- "关闭所有灯光"

### 温度控制
- "把空调温度调到26度"
- "打开客厅暖气"
- "空调调到制冷模式"

### 音响控制
- "播放轻音乐"
- "音量调大一点"
- "切换到下一首歌"
- "暂停音乐"

### 窗帘控制
- "打开卧室窗帘"
- "窗帘开一半"
- "关闭所有窗帘"

## 技术栈

- **语音识别**: OpenAI Whisper
- **NLP处理**: Transformers, BERT
- **Web框架**: FastAPI
- **实时通信**: WebSocket, MQTT
- **数据处理**: NumPy, SciPy, librosa
- **包管理**: uv
- **测试框架**: pytest

## 开发指南

### 添加新设备类型
1. 在 `src/smart_home/devices/` 下创建设备类
2. 实现设备控制接口
3. 在 NLU 模块中添加相关意图
4. 更新 API 路由

### 扩展语音指令
1. 在 `config/intents.json` 中定义新意图
2. 添加训练数据
3. 更新意图识别模型
4. 测试新指令

## 详细文档

### 📚 技术文档
- [实体抽取优化指南](docs/entity_extraction_optimization.md) - 全面的实体抽取优化方案和技术选型
- [BIO标注方案详解](docs/bio_tagging_guide.md) - 命名实体识别的BIO标注完整指南
- [混淆矩阵详解](docs/confusion_matrix_guide.md) - 模型评估中的混淆矩阵分析
- [评估指标详解](docs/evaluation_metrics.md) - 模型评估指标的详细说明

### 🛠️ 操作文档
- [使用指南](USAGE.md) - 详细的使用说明和配置指南
- [项目总结](PROJECT_SUMMARY.md) - 项目整体架构和实现总结

## 部署说明

详见 [部署文档](docs/deployment.md)

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 