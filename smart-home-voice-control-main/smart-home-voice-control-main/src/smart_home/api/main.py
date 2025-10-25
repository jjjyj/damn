"""
FastAPI 主应用 - 智能家居语音控制 API
"""

import io
import time
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import numpy as np
# soundfile: 用于读取和写入音频文件的库
# 支持多种音频格式 (WAV, FLAC, OGG, AIFF等)
# 提供高质量的音频处理功能，常用于语音识别预处理
import soundfile as sf

from ..core.config import settings
from ..core.models import (
    VoiceRequest, VoiceResponse, DeviceInfo, DeviceCommand, 
    DeviceResponse, SystemStatus, IntentType, DeviceType
)
from ..asr import asr_service
from ..nlu import nlu_service  
from ..devices import device_manager, SmartLight

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 启动智能家居语音控制系统")
    
    # 初始化 ASR 服务
    logger.info("正在初始化语音识别服务...")
    asr_service.load_model()
    
    # 注册示例设备
    logger.info("正在注册示例设备...")
    init_demo_devices()
    
    logger.info("✅ 系统初始化完成")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 正在关闭系统...")


def init_demo_devices():
    """初始化演示设备"""
    demo_devices = [
        SmartLight("light_living_room", "客厅吊灯", "客厅"),
        SmartLight("light_bedroom", "卧室台灯", "卧室"),
        SmartLight("light_kitchen", "厨房射灯", "厨房"),
        SmartLight("light_study", "书房台灯", "书房"),
    ]
    
    for device in demo_devices:
        device_manager.register_device(device)
    
    logger.info(f"已注册 {len(demo_devices)} 个演示设备")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="基于语音识别和自然语言理解的智能家居控制系统",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="系统信息")
async def root():
    """获取系统基本信息"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "running",
        "message": "智能家居语音控制系统正在运行"
    }


@app.get("/health", summary="健康检查")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "asr": asr_service.is_ready(),
            "nlu": True,  # NLU 服务总是可用
            "device_manager": len(device_manager.get_all_devices()) > 0
        }
    }


@app.post("/api/v1/voice/process", response_model=VoiceResponse, summary="处理语音指令")
async def process_voice_command(
    audio_file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    language: str = Form("zh")
):
    """
    处理语音指令的主要接口
    
    Args:
        audio_file: 音频文件 (支持 wav, mp3, m4a 等格式)
        user_id: 用户ID (可选)
        session_id: 会话ID (可选)
        language: 语言代码 (zh: 中文, en: 英文)
    """
    start_time = time.time()
    
    try:
        # 读取音频文件
        audio_bytes = await audio_file.read()
        
        # 使用 soundfile 解析音频
        audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        
        # 确保是单声道
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # 转换为 float32
        audio_data = audio_data.astype(np.float32)
        
        logger.info(f"接收到语音文件: {audio_file.filename}, 采样率: {sample_rate}")
        
        # 1. 语音识别 (ASR)
        asr_result = asr_service.transcribe_audio(audio_data, language)
        
        if not asr_result.text:
            return VoiceResponse(
                success=False,
                message="语音识别失败，请重试",
                processing_time=time.time() - start_time
            )
        
        logger.info(f"ASR 结果: {asr_result.text}")
        
        # 2. 自然语言理解 (NLU)
        nlu_result = nlu_service.process(asr_result.text)
        
        logger.info(f"NLU 结果: 意图={nlu_result.intent.intent}, 实体={len(nlu_result.intent.entities)}")
        
        # 3. 执行设备控制
        device_responses = await execute_smart_home_command(nlu_result)
        
        processing_time = time.time() - start_time
        
        return VoiceResponse(
            success=True,
            message="语音指令处理完成",
            recognized_text=asr_result.text,
            intent=nlu_result.intent,
            device_responses=device_responses,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"处理语音指令失败: {e}")
        return VoiceResponse(
            success=False,
            message=f"处理失败: {str(e)}",
            processing_time=time.time() - start_time
        )


async def execute_smart_home_command(nlu_result) -> List[DeviceResponse]:
    """
    根据 NLU 结果执行智能家居命令
    
    Args:
        nlu_result: NLU 处理结果
        
    Returns:
        设备响应列表
    """
    intent = nlu_result.intent
    entities = {e.entity: e.value for e in intent.entities}
    
    responses = []
    
    # 如果置信度太低，返回提示信息
    if intent.confidence < settings.intent_confidence_threshold:
        return [DeviceResponse(
            device_id="system",
            success=False,
            message="抱歉，我没有理解您的指令，请重新说一遍"
        )]
    
    # 根据意图类型执行相应操作，先对意图进行分类，然后在对每个意图里面的具体行为进行分类吗
    if intent.intent == IntentType.CONTROL_LIGHT:
        responses = await handle_light_control(entities)
    elif intent.intent == IntentType.QUERY_STATUS:
        responses = await handle_status_query(entities)
    elif intent.intent == IntentType.GENERAL_CHAT:
        responses = [DeviceResponse(
            device_id="system",
            success=True,
            message="您好！我是智能家居助手，可以帮您控制家中的设备"
        )]
    else:
        responses = [DeviceResponse(
            device_id="system",
            success=False,
            message=f"暂不支持 {intent.intent} 类型的操作"
        )]
    
    return responses


async def handle_light_control(entities: dict) -> List[DeviceResponse]:
    """处理灯光控制"""
    room = entities.get("room")
    action = entities.get("action")
    
    # 查找目标设备
    if room:
        devices = device_manager.find_devices(room=room, device_type=DeviceType.LIGHT)
    else:
        devices = device_manager.get_devices_by_type(DeviceType.LIGHT)
    
    if not devices:
        return [DeviceResponse(
            device_id="system",
            success=False,
            message=f"未找到{room or ''}的灯光设备"
        )]
    
    responses = []
    
    # 对每个设备进行处理，具体的行为操作，比如打开、关闭、设置亮度、设置颜色等
    for device in devices:
        if action == "turn_on":
            response = await device.turn_on()
        elif action == "turn_off":
            response = await device.turn_off()
        elif action == "set_brightness":
            brightness = int(entities.get("number", "50"))
            command = DeviceCommand(
                device_id=device.device_id,
                action="set_brightness",
                parameters={"brightness": brightness}
            )
            response = await device.execute_command(command)
        elif action == "set_color":
            color = entities.get("color", "白色")
            command = DeviceCommand(
                device_id=device.device_id,
                action="set_color",
                parameters={"color": color}
            )
            response = await device.execute_command(command)
        else:
            response = DeviceResponse(
                device_id=device.device_id,
                success=False,
                message=f"不支持的灯光操作: {action}"
            )
        
        responses.append(response)
    
    return responses


async def handle_status_query(entities: dict) -> List[DeviceResponse]:
    """处理状态查询"""
    room = entities.get("room")
    device_type = entities.get("device_type")
    
    # 查找设备
    devices = device_manager.find_devices(room=room)
    if device_type:
        device_type_enum = DeviceType(device_type) if device_type in [dt.value for dt in DeviceType] else None
        if device_type_enum:
            devices = [d for d in devices if d.device_type == device_type_enum]
    
    if not devices:
        return [DeviceResponse(
            device_id="system",
            success=False,
            message=f"未找到{room or ''}的设备"
        )]
    
    status_messages = []
    for device in devices:
        status = "开启" if device.status.get("power", False) else "关闭"
        status_messages.append(f"{device.room}{device.name}当前{status}")
    
    return [DeviceResponse(
        device_id="system",
        success=True,
        message="；".join(status_messages)
    )]


@app.get("/api/v1/devices", response_model=List[DeviceInfo], summary="获取所有设备")
async def get_all_devices():
    """获取所有注册的设备信息"""
    devices = device_manager.get_all_devices()
    return [device.get_info() for device in devices]


@app.get("/api/v1/devices/room/{room_name}", response_model=List[DeviceInfo], summary="获取房间设备")
async def get_devices_by_room(room_name: str):
    """获取指定房间的设备列表"""
    devices = device_manager.get_devices_by_room(room_name)
    return [device.get_info() for device in devices]


@app.post("/api/v1/devices/{device_id}/command", response_model=DeviceResponse, summary="执行设备命令")
async def execute_device_command(device_id: str, command: DeviceCommand):
    """直接执行设备命令"""
    command.device_id = device_id  # 确保设备ID正确
    return await device_manager.execute_command(command)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "smart_home.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    ) 