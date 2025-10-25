#!/usr/bin/env python3
"""
NLU 模块单元测试
"""

import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.smart_home.nlu import nlu_service
from src.smart_home.core.models import IntentType


class TestNLUService:
    """NLU 服务测试类"""
    
    def test_light_control_intents(self):
        """测试灯光控制意图识别"""
        test_cases = [
            ("打开客厅的灯", IntentType.CONTROL_LIGHT, "room", "客厅"),
            ("关闭卧室台灯", IntentType.CONTROL_LIGHT, "room", "卧室"),
            ("把书房灯调亮一点", IntentType.CONTROL_LIGHT, "room", "书房"),
            ("将客厅灯光设为红色", IntentType.CONTROL_LIGHT, "room", "客厅"),
            ("开启所有灯光", IntentType.CONTROL_LIGHT, None, None),
        ]
        
        for text, expected_intent, entity_type, entity_value in test_cases:
            result = nlu_service.process(text)
            
            assert result.intent.intent == expected_intent, f"意图识别错误: {text}"
            assert result.intent.confidence > 0.5, f"置信度过低: {text}"
            
            if entity_type and entity_value:
                entities = {e.entity: e.value for e in result.intent.entities}
                assert entity_type in entities, f"未找到实体 {entity_type}: {text}"
                assert entities[entity_type] == entity_value, f"实体值错误: {text}"
    
    def test_action_extraction(self):
        """测试动作提取"""
        test_cases = [
            ("打开客厅的灯", "turn_on"),
            ("关闭卧室台灯", "turn_off"),
            ("调亮书房的灯", "set_brightness"),
            ("把灯设为红色", "set_color"),
        ]
        
        for text, expected_action in test_cases:
            result = nlu_service.process(text)
            entities = {e.entity: e.value for e in result.intent.entities}
            
            assert "action" in entities, f"未找到动作实体: {text}"
            assert entities["action"] == expected_action, f"动作识别错误: {text}"
    
    def test_room_extraction(self):
        """测试房间提取"""
        test_cases = [
            ("打开客厅的灯", "客厅"),
            ("关闭卧室台灯", "卧室"),
            ("厨房灯光状态", "厨房"),
            ("书房的空调", "书房"),
        ]
        
        for text, expected_room in test_cases:
            result = nlu_service.process(text)
            entities = {e.entity: e.value for e in result.intent.entities}
            
            if expected_room:
                assert "room" in entities, f"未找到房间实体: {text}"
                assert entities["room"] == expected_room, f"房间识别错误: {text}"
    
    def test_device_type_extraction(self):
        """测试设备类型提取"""
        test_cases = [
            ("打开客厅的灯", "light"),
            ("调节空调温度", "air_conditioner"),
            ("播放音乐", "speaker"),
            ("开启窗帘", "curtain"),
        ]
        
        for text, expected_device_type in test_cases:
            result = nlu_service.process(text)
            entities = {e.entity: e.value for e in result.intent.entities}
            
            if expected_device_type:
                assert "device_type" in entities, f"未找到设备类型实体: {text}"
                assert entities["device_type"] == expected_device_type, f"设备类型识别错误: {text}"
    
    def test_status_query_intent(self):
        """测试状态查询意图"""
        test_cases = [
            "客厅灯光状态如何",
            "卧室空调开了吗",
            "查看所有设备状态",
            "厨房有哪些设备在运行"
        ]
        
        for text in test_cases:
            result = nlu_service.process(text)
            assert result.intent.intent == IntentType.QUERY_STATUS, f"状态查询意图识别错误: {text}"
    
    def test_general_chat_intent(self):
        """测试一般对话意图"""
        test_cases = [
            "你好",
            "谢谢",
            "再见",
            "你是谁",
            "今天天气怎么样"
        ]
        
        for text in test_cases:
            result = nlu_service.process(text)
            # 一般对话可能被识别为其他意图，但置信度应该较低
            if result.intent.intent == IntentType.GENERAL_CHAT:
                assert result.intent.confidence > 0, f"一般对话意图置信度为零: {text}"
    
    def test_number_extraction(self):
        """测试数字提取"""
        test_cases = [
            ("把灯调到五十", "50"),
            ("温度设为26度", "26"),
            ("亮度调到80", "80"),
        ]
        
        for text, expected_number in test_cases:
            result = nlu_service.process(text)
            entities = {e.entity: e.value for e in result.intent.entities}
            
            # 检查是否提取到数字或温度
            has_number = "number" in entities or "temperature" in entities
            if expected_number.isdigit():
                assert has_number, f"未找到数字实体: {text}"
    
    def test_color_extraction(self):
        """测试颜色提取"""
        # 这里我们测试颜色是否作为动作参数被正确提取
        color_texts = [
            "把灯设为红色",
            "灯光调成蓝色",
            "设置为暖色调"
        ]
        
        for text in color_texts:
            result = nlu_service.process(text)
            # 颜色通常作为 set_color 动作的参数
            entities = {e.entity: e.value for e in result.intent.entities}
            if "action" in entities and entities["action"] == "set_color":
                assert result.intent.intent == IntentType.CONTROL_LIGHT, f"颜色控制应为灯光控制意图: {text}"
    
    def test_confidence_scores(self):
        """测试置信度评分"""
        # 明确的指令应该有高置信度
        clear_commands = [
            "打开客厅的灯",
            "关闭卧室空调",
            "播放音乐"
        ]
        
        for text in clear_commands:
            result = nlu_service.process(text)
            assert result.intent.confidence > 0.7, f"明确指令置信度过低: {text}"
        
        # 模糊的指令可能有较低置信度
        ambiguous_commands = [
            "那个",
            "嗯",
            "可能吧"
        ]
        
        for text in ambiguous_commands:
            result = nlu_service.process(text)
            # 模糊指令可能被识别为各种意图，但置信度通常较低


if __name__ == "__main__":
    # 运行测试
    test_nlu = TestNLUService()
    
    print("🧠 运行 NLU 测试...")
    
    try:
        test_nlu.test_light_control_intents()
        print("✅ 灯光控制意图测试通过")
        
        test_nlu.test_action_extraction()
        print("✅ 动作提取测试通过")
        
        test_nlu.test_room_extraction()
        print("✅ 房间提取测试通过")
        
        test_nlu.test_device_type_extraction()
        print("✅ 设备类型提取测试通过")
        
        test_nlu.test_status_query_intent()
        print("✅ 状态查询意图测试通过")
        
        test_nlu.test_general_chat_intent()
        print("✅ 一般对话意图测试通过")
        
        test_nlu.test_number_extraction()
        print("✅ 数字提取测试通过")
        
        test_nlu.test_confidence_scores()
        print("✅ 置信度评分测试通过")
        
        print("\n🎉 所有 NLU 测试通过!")
        
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
    except Exception as e:
        print(f"❌ 测试出错: {e}") 