"""
系统配置管理模块
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用程序配置"""
    
    # 基本配置
    app_name: str = "智能家居语音控制系统"
    version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # API 配置
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = "/api/v1"
    
    # 语音识别配置
    whisper_model: str = Field(default="base", env="WHISPER_MODEL")  # tiny, base, small, medium, large
    audio_sample_rate: int = 16000
    audio_chunk_duration: float = 1.0  # seconds
    
    # NLU 配置
    nlu_model_path: Optional[str] = Field(default=None, env="NLU_MODEL_PATH")
    intent_confidence_threshold: float = 0.7
    
    # 设备配置
    mqtt_broker_host: str = Field(default="localhost", env="MQTT_HOST")
    mqtt_broker_port: int = Field(default=1883, env="MQTT_PORT")
    mqtt_username: Optional[str] = Field(default=None, env="MQTT_USERNAME")
    mqtt_password: Optional[str] = Field(default=None, env="MQTT_PASSWORD")
    
    # 支持的房间
    supported_rooms: List[str] = [
        "客厅", "卧室", "厨房", "书房", "卫生间", "阳台", "主卧", "次卧"
    ]
    
    # 支持的设备类型
    supported_device_types: List[str] = [
        "灯光", "空调", "暖气", "音响", "窗帘", "门锁", "摄像头", "传感器"
    ]
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # 安全配置
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings() 