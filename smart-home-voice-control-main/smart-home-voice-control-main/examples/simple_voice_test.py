#!/usr/bin/env python3
"""
简单的语音控制测试示例

演示如何使用智能家居语音控制系统的基本功能。
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.smart_home.asr import asr_service
from src.smart_home.nlu import nlu_service
from src.smart_home.devices import device_manager, SmartLight
from src.smart_home.core.models import DeviceCommand, DeviceAction


async def setup_demo_devices():
    """设置演示设备"""
    print("🏠 正在初始化演示设备...")
    
    # 创建一些演示设备
    devices = [
        SmartLight("light_001", "客厅主灯", "客厅"),
        SmartLight("light_002", "卧室台灯", "卧室"),
        SmartLight("light_003", "厨房射灯", "厨房"),
    ]
    
    # 注册设备
    for device in devices:
        device_manager.register_device(device)
    
    print(f"✅ 已注册 {len(devices)} 个设备")
    return devices


async def test_text_commands():
    """测试文本命令处理"""
    print("\n🧠 测试文本命令处理...")
    
    test_commands = [
        "打开客厅的灯",
        "关闭卧室台灯", 
        "把厨房灯调亮一点",
        "将客厅灯设为红色",
        "查看客厅设备状态"
    ]
    
    for command_text in test_commands:
        print(f"\n📝 处理指令: '{command_text}'")
        
        # NLU 处理
        nlu_result = nlu_service.process(command_text)
        print(f"   意图: {nlu_result.intent.intent}")
        print(f"   置信度: {nlu_result.intent.confidence:.2f}")
        print(f"   实体: {[(e.entity, e.value) for e in nlu_result.intent.entities]}")
        
        # 模拟设备控制
        await simulate_device_control(nlu_result)


async def simulate_device_control(nlu_result):
    """模拟设备控制"""
    intent = nlu_result.intent
    entities = {e.entity: e.value for e in intent.entities}
    
    # 查找目标设备
    room = entities.get("room")
    if room:
        devices = device_manager.get_devices_by_room(room)
    else:
        devices = device_manager.get_all_devices()
    
    if not devices:
        print(f"   ❌ 未找到设备")
        return
    
    # 执行命令
    action = entities.get("action")
    for device in devices:
        if action == "turn_on":
            response = await device.turn_on()
        elif action == "turn_off":
            response = await device.turn_off()
        elif action == "set_brightness":
            command = DeviceCommand(
                device_id=device.device_id,
                action=DeviceAction.SET_BRIGHTNESS,
                parameters={"brightness": 80}
            )
            response = await device.execute_command(command)
        elif action == "set_color":
            command = DeviceCommand(
                device_id=device.device_id,
                action=DeviceAction.SET_COLOR,
                parameters={"color": "红色"}
            )
            response = await device.execute_command(command)
        else:
            # 查询状态
            status = "开启" if device.status.get("power", False) else "关闭"
            print(f"   📊 {device.name} 当前状态: {status}")
            continue
        
        print(f"   ✅ {response.message}")


async def test_asr_if_available():
    """如果可能的话测试 ASR"""
    print("\n🎤 检查语音识别服务...")
    
    try:
        # 尝试加载 ASR 模型
        asr_service.load_model()
        print("✅ ASR 服务已就绪")
        
        # 这里可以添加音频文件测试
        # 但需要实际的音频文件
        print("💡 您可以通过 API 接口上传音频文件进行测试")
        
    except Exception as e:
        print(f"⚠️  ASR 服务不可用: {e}")
        print("💡 这是正常的，因为 Whisper 模型需要额外下载")


async def display_system_status():
    """显示系统状态"""
    print("\n📊 系统状态:")
    print(f"   注册设备数量: {len(device_manager.get_all_devices())}")
    print(f"   ASR 服务状态: {'就绪' if asr_service.is_ready() else '未就绪'}")
    print(f"   NLU 服务状态: 就绪")
    
    print("\n📋 设备列表:")
    for device in device_manager.get_all_devices():
        status = "🟢 开启" if device.status.get("power", False) else "🔴 关闭"
        print(f"   {device.room} - {device.name}: {status}")


async def main():
    """主函数"""
    print("🚀 智能家居语音控制系统 - 测试示例")
    print("=" * 50)
    
    # 设置演示设备
    await setup_demo_devices()
    
    # 测试文本命令处理
    await test_text_commands()
    
    # 测试 ASR (如果可用)
    await test_asr_if_available()
    
    # 显示系统状态
    await display_system_status()
    
    print("\n✅ 测试完成!")
    print("\n💡 提示:")
    print("   1. 运行 'uv run python -m smart_home.api.main' 启动 API 服务")
    print("   2. 访问 http://localhost:8000/docs 查看 API 文档")
    print("   3. 使用 /api/v1/voice/process 接口上传音频文件进行语音控制")


if __name__ == "__main__":
    asyncio.run(main()) 