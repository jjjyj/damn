#!/usr/bin/env python3
"""
智能家居系统演示 - 无需语音识别依赖

展示文本命令处理和设备控制功能。
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.smart_home.nlu import nlu_service
from src.smart_home.devices import device_manager, SmartLight
from src.smart_home.core.models import DeviceCommand, DeviceAction


async def setup_demo_environment():
    """设置演示环境"""
    print("🏠 初始化智能家居演示环境...")
    
    # 创建演示设备
    devices = [
        SmartLight("light_living_room", "客厅主灯", "客厅"),
        SmartLight("light_bedroom", "卧室台灯", "卧室"),
        SmartLight("light_kitchen", "厨房射灯", "厨房"),
        SmartLight("light_study", "书房吊灯", "书房"),
    ]
    
    # 注册设备
    for device in devices:
        device_manager.register_device(device)
    
    print(f"✅ 已注册 {len(devices)} 个演示设备")
    
    # 显示初始状态
    print("\n📋 设备初始状态:")
    for device in devices:
        status = "🟢 开启" if device.status.get("power", False) else "🔴 关闭"
        print(f"   {device.room} - {device.name}: {status}")


async def demo_voice_commands():
    """演示语音命令处理"""
    print("\n🎤 智能家居语音命令演示")
    print("=" * 50)
    
    # 演示命令列表
    demo_commands = [
        "打开客厅的灯",
        "关闭卧室台灯",
        "把厨房灯调亮一点",
        "将书房灯设为蓝色",
        "查看客厅设备状态",
        "关闭所有灯光",
        "你好，智能助手"
    ]
    
    for i, command_text in enumerate(demo_commands, 1):
        print(f"\n🗣️  指令 {i}: '{command_text}'")
        print("-" * 40)
        
        # 1. NLU 处理
        nlu_result = nlu_service.process(command_text)
        print(f"🧠 意图识别: {nlu_result.intent.intent}")
        print(f"🎯 置信度: {nlu_result.intent.confidence:.2f}")
        
        if nlu_result.intent.entities:
            print("🏷️  提取实体:")
            for entity in nlu_result.intent.entities:
                print(f"     {entity.entity}: {entity.value}")
        
        # 2. 设备控制
        device_responses = await simulate_device_control(nlu_result)
        
        print("🤖 执行结果:")
        for response in device_responses:
            if response.success:
                print(f"     ✅ {response.message}")
            else:
                print(f"     ❌ {response.message}")
        
        # 添加延迟使演示更清晰
        await asyncio.sleep(0.5)


async def simulate_device_control(nlu_result):
    """模拟设备控制"""
    intent = nlu_result.intent
    entities = {e.entity: e.value for e in intent.entities}
    
    responses = []
    
    # 根据意图执行相应操作
    if intent.intent.value == "control_light":
        responses = await handle_light_control(entities)
    elif intent.intent.value == "query_status":
        responses = await handle_status_query(entities)
    elif intent.intent.value == "general_chat":
        responses = [type('DeviceResponse', (), {
            'device_id': 'system',
            'success': True,
            'message': '您好！我是智能家居助手，很高兴为您服务！'
        })()]
    else:
        responses = [type('DeviceResponse', (), {
            'device_id': 'system',
            'success': False,
            'message': f'暂不支持 {intent.intent} 类型的操作'
        })()]
    
    return responses


async def handle_light_control(entities):
    """处理灯光控制"""
    room = entities.get("room")
    action = entities.get("action")
    
    # 查找目标设备
    if room:
        devices = device_manager.get_devices_by_room(room)
    else:
        # 如果是"所有"设备
        devices = device_manager.get_all_devices()
    
    if not devices:
        return [type('DeviceResponse', (), {
            'device_id': 'system',
            'success': False,
            'message': f'未找到{room or ""}的灯光设备'
        })()]
    
    responses = []
    
    for device in devices:
        if action == "turn_on":
            response = await device.turn_on()
        elif action == "turn_off":
            response = await device.turn_off()
        elif action == "set_brightness":
            brightness = int(entities.get("number", "80"))
            command = DeviceCommand(
                device_id=device.device_id,
                action=DeviceAction.SET_BRIGHTNESS,
                parameters={"brightness": brightness}
            )
            response = await device.execute_command(command)
        elif action == "set_color":
            color = entities.get("color", "蓝色")
            command = DeviceCommand(
                device_id=device.device_id,
                action=DeviceAction.SET_COLOR,
                parameters={"color": color}
            )
            response = await device.execute_command(command)
        else:
            response = type('DeviceResponse', (), {
                'device_id': device.device_id,
                'success': False,
                'message': f'不支持的灯光操作: {action}'
            })()
        
        responses.append(response)
    
    return responses


async def handle_status_query(entities):
    """处理状态查询"""
    room = entities.get("room")
    
    # 查找设备
    if room:
        devices = device_manager.get_devices_by_room(room)
    else:
        devices = device_manager.get_all_devices()
    
    if not devices:
        return [type('DeviceResponse', (), {
            'device_id': 'system',
            'success': False,
            'message': f'未找到{room or ""}的设备'
        })()]
    
    status_messages = []
    for device in devices:
        power_status = "开启" if device.status.get("power", False) else "关闭"
        brightness = device.status.get("brightness", 0)
        color = device.status.get("color", "#FFFFFF")
        
        status_detail = f"{device.room}{device.name}当前{power_status}"
        if device.status.get("power", False):
            status_detail += f"，亮度{brightness}%"
        status_messages.append(status_detail)
    
    return [type('DeviceResponse', (), {
        'device_id': 'system',
        'success': True,
        'message': '；'.join(status_messages)
    })()]


async def show_final_status():
    """显示最终设备状态"""
    print("\n📊 演示结束后的设备状态:")
    print("=" * 50)
    
    devices = device_manager.get_all_devices()
    for device in devices:
        power_status = "🟢 开启" if device.status.get("power", False) else "🔴 关闭"
        brightness = device.status.get("brightness", 0)
        color = device.status.get("color", "#FFFFFF")
        
        print(f"{device.room} - {device.name}: {power_status}")
        if device.status.get("power", False):
            print(f"   💡 亮度: {brightness}%")
            print(f"   🎨 颜色: {color}")


async def main():
    """主函数"""
    print("🚀 智能家居语音控制系统 - 功能演示")
    print("🎯 本演示将展示文本命令处理和设备控制功能")
    print("=" * 60)
    
    # 设置演示环境
    await setup_demo_environment()
    
    # 演示语音命令处理
    await demo_voice_commands()
    
    # 显示最终状态
    await show_final_status()
    
    print("\n🎉 演示完成！")
    print("\n💡 接下来您可以:")
    print("   1. 运行 'python start_server.py' 启动完整的API服务")
    print("   2. 安装 whisper 模块体验语音识别功能")
    print("   3. 查看 USAGE.md 了解更多使用方法")


if __name__ == "__main__":
    asyncio.run(main()) 