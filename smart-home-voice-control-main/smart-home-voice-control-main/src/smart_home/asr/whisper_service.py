"""
基于 OpenAI Whisper 的语音识别服务
"""

import time
import numpy as np
import whisper
import torch
from typing import Optional, Union
import logging

from ..core.config import settings
from ..core.models import ASRResult, AudioInput

logger = logging.getLogger(__name__)


class WhisperASRService:
    """Whisper 语音识别服务"""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        初始化 Whisper ASR 服务
        
        Args:
            model_name: Whisper 模型名称 (tiny, base, small, medium, large)
        """
        self.model_name = model_name or settings.whisper_model
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"ASR 服务将使用设备: {self.device}")
        
    def load_model(self) -> None:
        """加载 Whisper 模型"""
        if self.model is None:
            logger.info(f"正在加载 Whisper 模型: {self.model_name}")
            try:
                self.model = whisper.load_model(self.model_name, device=self.device)
                logger.info("Whisper 模型加载成功")
            except Exception as e:
                logger.error(f"加载 Whisper 模型失败: {e}")
                raise
    
    def transcribe_audio(
        self, 
        audio_data: Union[np.ndarray, str, AudioInput],
        language: str = "zh"
    ) -> ASRResult:
        """
        转录音频数据
        
        Args:
            audio_data: 音频数据 (numpy数组、文件路径或AudioInput对象)
            language: 语言代码 (zh: 中文, en: 英文)
            
        Returns:
            ASRResult: 识别结果
        """
        start_time = time.time()
        
        if self.model is None:
            self.load_model()
        
        try:
            # 处理不同类型的音频输入
            if isinstance(audio_data, AudioInput):
                # 从 AudioInput 对象提取音频数据
                audio = np.frombuffer(audio_data.audio_data, dtype=np.float32)
            elif isinstance(audio_data, str):
                # 文件路径
                audio = whisper.load_audio(audio_data)
            else:
                # numpy 数组
                audio = audio_data
            
            # 确保音频数据是正确的格式
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # 归一化音频数据到 [-1, 1] 范围
            if audio.max() > 1.0 or audio.min() < -1.0:
                audio = audio / np.max(np.abs(audio))
            
            # 执行语音转录：将音频信号转换为文本
            # 这是语音识别(ASR)的核心步骤，将用户的语音输入转换为可理解的文本
            # 参数说明：
            # - audio: 预处理后的音频数据
            # - language: 指定语言以提高识别准确率
            # - task="transcribe": 执行转录任务（区别于翻译任务）
            # - verbose=False: 关闭详细输出以提高性能
            logger.debug(f"开始转录音频，语言: {language}")
            result = self.model.transcribe(
                audio, 
                language=language,
                task="transcribe",
                verbose=False
            )
            
            processing_time = time.time() - start_time
            
            # 提取文本和置信度
            text = result["text"].strip()
            
            # Whisper 不直接提供置信度，这里使用一个简单的估算
            # segments 是 Whisper 模型返回的音频分段信息列表
            # 每个 segment 包含该时间段的转录文本、时间戳、置信度等信息
            # 用于计算整体转录的置信度和时间对齐
            segments = result.get("segments", [])
            if segments:
                # 计算平均 logprob 作为置信度的近似
                avg_logprob = np.mean([seg.get("avg_logprob", -1.0) for seg in segments])
                confidence = min(1.0, max(0.0, np.exp(avg_logprob)))
            else:
                confidence = 0.8 if text else 0.0
            
            logger.info(f"ASR 转录完成: '{text}' (置信度: {confidence:.2f}, 耗时: {processing_time:.2f}s)")
            
            return ASRResult(
                text=text,
                confidence=confidence,
                language=language,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"音频转录失败: {e}")
            processing_time = time.time() - start_time
            return ASRResult(
                text="",
                confidence=0.0,
                language=language,
                processing_time=processing_time
            )
    
    def transcribe_file(self, file_path: str, language: str = "zh") -> ASRResult:
        """
        转录音频文件
        
        Args:
            file_path: 音频文件路径
            language: 语言代码
            
        Returns:
            ASRResult: 识别结果
        """
        return self.transcribe_audio(file_path, language)
    
    def is_ready(self) -> bool:
        """检查服务是否就绪"""
        return self.model is not None
    
    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        if self.model is None:
            self.load_model()
        return list(self.model.tokenizer.language_names.keys())


# 全局 ASR 服务实例
asr_service = WhisperASRService() 