"""
数据模型定义
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """设备类型枚举"""
    LIGHT = "light"
    AIR_CONDITIONER = "air_conditioner"
    HEATER = "heater"
    SPEAKER = "speaker"
    CURTAIN = "curtain"
    DOOR_LOCK = "door_lock"
    CAMERA = "camera"
    SENSOR = "sensor"


class DeviceAction(str, Enum):
    """设备动作枚举"""
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    SET_BRIGHTNESS = "set_brightness"
    SET_COLOR = "set_color"
    SET_TEMPERATURE = "set_temperature"
    SET_VOLUME = "set_volume"
    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"
    OPEN = "open"
    CLOSE = "close"
    LOCK = "lock"
    UNLOCK = "unlock"


class IntentType(str, Enum):
    """意图类型枚举"""
    CONTROL_LIGHT = "control_light"          # 控制灯光开关、亮度、颜色等
    CONTROL_TEMPERATURE = "control_temperature"  # 控制空调、暖气等温控设备
    CONTROL_MUSIC = "control_music"          # 控制音响、播放音乐等音频设备
    CONTROL_CURTAIN = "control_curtain"      # 控制窗帘开关
    CONTROL_SECURITY = "control_security"    # 控制门锁、摄像头等安防设备
    QUERY_STATUS = "query_status"            # 查询设备状态信息
    GENERAL_CHAT = "general_chat"            # 通用对话，非设备控制意图


# ASR 相关模型
class AudioInput(BaseModel):
    """音频输入模型"""
    audio_data: bytes
    sample_rate: int = 16000
    format: str = "wav"
    timestamp: datetime = Field(default_factory=datetime.now)


class ASRResult(BaseModel):
    """语音识别结果"""
    text: str
    confidence: float
    language: str = "zh"
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.now)


# NLU 相关模型
class Entity(BaseModel):
    """实体提取结果"""
    entity: str
    value: str
    confidence: float
    start: int
    end: int


class Intent(BaseModel):
    """意图识别结果"""
    intent: IntentType
    confidence: float
    entities: List[Entity] = []


class NLUResult(BaseModel):
    """NLU 处理结果"""
    text: str
    intent: Intent
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.now)


# 设备相关模型
class DeviceInfo(BaseModel):
    """设备信息"""
    device_id: str
    name: str
    device_type: DeviceType
    room: str
    brand: Optional[str] = None
    model: Optional[str] = None
    status: Dict[str, Any] = Field(default_factory=dict)
    is_online: bool = True
    last_update: datetime = Field(default_factory=datetime.now)


class DeviceCommand(BaseModel):
    """设备控制命令"""
    device_id: str
    action: DeviceAction
    parameters: Dict[str, Any] = Field(default_factory=dict)
    room: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class DeviceResponse(BaseModel):
    """设备响应"""
    device_id: str
    success: bool
    message: str
    new_status: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# API 相关模型
class VoiceRequest(BaseModel):
    """语音请求模型"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    audio_format: str = "wav"
    sample_rate: int = 16000


class VoiceResponse(BaseModel):
    """语音响应模型"""
    success: bool
    message: str
    recognized_text: Optional[str] = None
    intent: Optional[Intent] = None
    device_responses: List[DeviceResponse] = []
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemStatus(BaseModel):
    """系统状态"""
    service_name: str
    status: str  # "running", "stopped", "error"
    uptime: float
    last_check: datetime = Field(default_factory=datetime.now)
    details: Dict[str, Any] = Field(default_factory=dict) 