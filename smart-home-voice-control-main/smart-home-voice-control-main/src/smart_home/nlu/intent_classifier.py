"""
意图分类器 - 理解用户语音指令的意图
"""

import re
import time
import json
from typing import Dict, List, Optional, Tuple
import logging

from ..core.config import settings
from ..core.models import Entity, Intent, IntentType, NLUResult

logger = logging.getLogger(__name__)


class SmartHomeIntentClassifier:
    """智能家居意图分类器"""
    
    def __init__(self):
        """初始化意图分类器"""
        self.room_patterns = self._build_room_patterns()
        self.device_patterns = self._build_device_patterns()
        self.action_patterns = self._build_action_patterns()
        self.number_patterns = self._build_number_patterns()
        
    def _build_room_patterns(self) -> Dict[str, List[str]]:
        """构建房间识别模式"""
        return {
            "客厅": ["客厅", "大厅", "起居室", "会客厅"],
            "卧室": ["卧室", "主卧", "次卧", "睡房", "房间"],
            "厨房": ["厨房", "灶台", "料理台"],
            "书房": ["书房", "办公室", "工作室", "学习室"],
            "卫生间": ["卫生间", "厕所", "洗手间", "浴室"],
            "阳台": ["阳台", "露台", "天台"],
        }
    
    def _build_device_patterns(self) -> Dict[str, List[str]]:
        """构建设备识别模式"""
        return {
            "light": ["灯", "灯光", "照明", "台灯", "吊灯", "壁灯", "射灯"],
            "air_conditioner": ["空调", "冷气", "制冷", "制暖", "调温"],
            "heater": ["暖气", "暖风", "取暖器", "电暖"],
            "speaker": ["音响", "音箱", "播放器", "扬声器", "喇叭"],
            "curtain": ["窗帘", "百叶窗", "遮光帘", "纱帘"],
            "door_lock": ["门锁", "大门", "房门", "锁"],
        }
    
    def _build_action_patterns(self) -> Dict[str, List[str]]:
        """构建动作识别模式"""
        return {
            "turn_on": ["打开", "开启", "启动", "开", "亮"],
            "turn_off": ["关闭", "关掉", "停止", "关", "灭"],
            "set_brightness": ["调亮", "调暗", "亮度", "明亮", "暗一点", "亮一点"],
            "set_color": ["颜色", "红色", "蓝色", "绿色", "黄色", "白色", "暖色", "冷色"],
            "set_temperature": ["温度", "度", "调温", "热一点", "冷一点"],
            "set_volume": ["音量", "声音", "大声", "小声", "音量大", "音量小"],
            "play": ["播放", "放", "播", "听"],
            "pause": ["暂停", "停", "停止播放"],
            "open": ["打开", "开启", "拉开"],
            "close": ["关闭", "关上", "拉上"],
        }
    
    def _build_number_patterns(self) -> Dict[str, int]:
        """构建数字识别模式"""
        return {
            "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
            "二十": 20, "三十": 30, "四十": 40, "五十": 50,
            "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
            "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
            "20": 20, "30": 30, "40": 40, "50": 50,
        }
    
    def extract_entities(self, text: str) -> List[Entity]:
        """提取实体信息"""
        entities = []
        
        # 提取房间实体
        for room, patterns in self.room_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    start = text.find(pattern)
                    entities.append(Entity(
                        entity="room",
                        value=room,
                        confidence=0.9,
                        start=start,
                        end=start + len(pattern)
                    ))
                    break
        
        # 提取设备类型实体
        for device_type, patterns in self.device_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    start = text.find(pattern)
                    entities.append(Entity(
                        entity="device_type",
                        value=device_type,
                        confidence=0.9,
                        start=start,
                        end=start + len(pattern)
                    ))
                    break
        
        # 提取动作实体
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    start = text.find(pattern)
                    entities.append(Entity(
                        entity="action",
                        value=action,
                        confidence=0.9,
                        start=start,
                        end=start + len(pattern)
                    ))
                    break
        
        # 提取数值实体
        for number_text, number_value in self.number_patterns.items():
            if number_text in text:
                start = text.find(number_text)
                entities.append(Entity(
                    entity="number",
                    value=str(number_value),
                    confidence=0.8,
                    start=start,
                    end=start + len(number_text)
                ))
        
        # 提取温度数值
        temp_match = re.search(r'(\d+)\s*度', text)
        if temp_match:
            start = temp_match.start()
            entities.append(Entity(
                entity="temperature",
                value=temp_match.group(1),
                confidence=0.9,
                start=start,
                end=temp_match.end()
            ))
        
        return entities
    
    def classify_intent(self, text: str) -> Intent:
        """分类用户意图"""
        text = text.lower()
        entities = self.extract_entities(text)
        
        # 根据实体和关键词确定意图
        device_entities = [e for e in entities if e.entity == "device_type"]
        action_entities = [e for e in entities if e.entity == "action"]
        
        if not device_entities:
            return Intent(
                intent=IntentType.GENERAL_CHAT,
                confidence=0.5,
                entities=entities
            )
        
        device_type = device_entities[0].value
        
        # 根据设备类型和动作确定意图
        if device_type == "light":
            intent_type = IntentType.CONTROL_LIGHT
            confidence = 0.9
        elif device_type in ["air_conditioner", "heater"]:
            intent_type = IntentType.CONTROL_TEMPERATURE  
            confidence = 0.9
        elif device_type == "speaker":
            intent_type = IntentType.CONTROL_MUSIC
            confidence = 0.9
        elif device_type == "curtain":
            intent_type = IntentType.CONTROL_CURTAIN
            confidence = 0.9
        elif device_type == "door_lock":
            intent_type = IntentType.CONTROL_SECURITY
            confidence = 0.9
        else:
            intent_type = IntentType.GENERAL_CHAT
            confidence = 0.3
        
        # 检查是否为状态查询
        if any(word in text for word in ["状态", "怎么样", "如何", "是否", "查看"]):
            intent_type = IntentType.QUERY_STATUS
            confidence = 0.8
        
        return Intent(
            intent=intent_type,
            confidence=confidence,
            entities=entities
        )
    
    def process(self, text: str) -> NLUResult:
        """处理自然语言输入"""
        start_time = time.time()
        
        logger.debug(f"开始 NLU 处理: '{text}'")
        
        try:
            intent = self.classify_intent(text)
            processing_time = time.time() - start_time
            
            logger.info(f"NLU 处理完成: 意图={intent.intent}, 置信度={intent.confidence:.2f}")
            
            return NLUResult(
                text=text,
                intent=intent,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"NLU 处理失败: {e}")
            processing_time = time.time() - start_time
            
            return NLUResult(
                text=text,
                intent=Intent(
                    intent=IntentType.GENERAL_CHAT,
                    confidence=0.0,
                    entities=[]
                ),
                processing_time=processing_time
            )


# 全局 NLU 服务实例
nlu_service = SmartHomeIntentClassifier() 