#!/usr/bin/env python3
"""
API 客户端使用示例

演示如何通过 HTTP API 与智能家居语音控制系统交互。
"""

import requests
import json
import asyncio
import time
from pathlib import Path


class SmartHomeAPIClient:
    """智能家居 API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化 API 客户端
        
        Args:
            base_url: API 服务器地址
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_health(self) -> dict:
        """检查系统健康状态"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_all_devices(self) -> list:
        """获取所有设备信息"""
        response = self.session.get(f"{self.base_url}/api/v1/devices")
        response.raise_for_status()
        return response.json()
    
    def get_devices_by_room(self, room_name: str) -> list:
        """获取指定房间的设备"""
        response = self.session.get(f"{self.base_url}/api/v1/devices/room/{room_name}")
        response.raise_for_status()
        return response.json()
    
    def execute_device_command(self, device_id: str, action: str, parameters: dict = None) -> dict:
        """执行设备命令"""
        command_data = {
            "device_id": device_id,
            "action": action,
            "parameters": parameters or {}
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/devices/{device_id}/command",
            json=command_data
        )
        response.raise_for_status()
        return response.json()
    
    def process_voice_command(self, audio_file_path: str, language: str = "zh") -> dict:
        """处理语音命令"""
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio_file': audio_file}
            data = {'language': language}
            
            response = self.session.post(
                f"{self.base_url}/api/v1/voice/process",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()


def test_api_connection():
    """测试 API 连接"""
    print("🔌 测试 API 连接...")
    
    client = SmartHomeAPIClient()
    
    try:
        health = client.check_health()
        print(f"✅ API 服务正常: {health['status']}")
        print(f"   服务状态: {health['services']}")
        return client
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 API 服务")
        print("💡 请确保 API 服务正在运行: uv run python -m smart_home.api.main")
        return None
    except Exception as e:
        print(f"❌ API 连接失败: {e}")
        return None


def test_device_management(client: SmartHomeAPIClient):
    """测试设备管理功能"""
    print("\n📱 测试设备管理功能...")
    
    try:
        # 获取所有设备
        devices = client.get_all_devices()
        print(f"✅ 获取到 {len(devices)} 个设备")
        
        for device in devices:
            print(f"   📱 {device['room']} - {device['name']} ({device['device_type']})")
            status = "🟢 开启" if device['status'].get('power', False) else "🔴 关闭"
            print(f"      状态: {status}")
        
        # 测试房间设备查询
        if devices:
            first_room = devices[0]['room']
            room_devices = client.get_devices_by_room(first_room)
            print(f"\n🏠 {first_room} 有 {len(room_devices)} 个设备")
        
    except Exception as e:
        print(f"❌ 设备管理测试失败: {e}")


def test_device_control(client: SmartHomeAPIClient):
    """测试设备控制功能"""
    print("\n🎛️ 测试设备控制功能...")
    
    try:
        devices = client.get_all_devices()
        if not devices:
            print("⚠️ 没有可用设备进行测试")
            return
        
        # 选择第一个灯光设备进行测试
        light_device = None
        for device in devices:
            if device['device_type'] == 'light':
                light_device = device
                break
        
        if not light_device:
            print("⚠️ 没有找到灯光设备进行测试")
            return
        
        device_id = light_device['device_id']
        device_name = light_device['name']
        
        print(f"🔍 测试设备: {device_name}")
        
        # 测试开灯
        print("   💡 开灯...")
        response = client.execute_device_command(device_id, "turn_on")
        print(f"   ✅ {response['message']}")
        
        time.sleep(1)
        
        # 测试调节亮度
        print("   🔆 调节亮度到 60%...")
        response = client.execute_device_command(
            device_id, "set_brightness", {"brightness": 60}
        )
        print(f"   ✅ {response['message']}")
        
        time.sleep(1)
        
        # 测试变色
        print("   🌈 设置为蓝色...")
        response = client.execute_device_command(
            device_id, "set_color", {"color": "蓝色"}
        )
        print(f"   ✅ {response['message']}")
        
        time.sleep(1)
        
        # 测试关灯
        print("   💤 关灯...")
        response = client.execute_device_command(device_id, "turn_off")
        print(f"   ✅ {response['message']}")
        
    except Exception as e:
        print(f"❌ 设备控制测试失败: {e}")


def test_voice_processing(client: SmartHomeAPIClient):
    """测试语音处理功能 (需要音频文件)"""
    print("\n🎤 测试语音处理功能...")
    
    # 这里我们只演示如何调用，实际需要音频文件
    print("💡 语音处理需要实际的音频文件")
    print("   您可以录制包含以下指令的音频:")
    print("   - '打开客厅的灯'")
    print("   - '关闭卧室台灯'")
    print("   - '把灯调亮一点'")
    print("   - '查看设备状态'")
    
    # 示例代码 (需要实际音频文件):
    # try:
    #     audio_file = "path/to/your/audio.wav"
    #     if Path(audio_file).exists():
    #         result = client.process_voice_command(audio_file)
    #         print(f"✅ 语音识别结果: {result['recognized_text']}")
    #         print(f"   意图: {result['intent']['intent']}")
    #         print(f"   设备响应: {[r['message'] for r in result['device_responses']]}")
    # except Exception as e:
    #     print(f"❌ 语音处理失败: {e}")


def main():
    """主函数"""
    print("🚀 智能家居 API 客户端测试")
    print("=" * 50)
    
    # 测试 API 连接
    client = test_api_connection()
    if not client:
        return
    
    # 测试设备管理
    test_device_management(client)
    
    # 测试设备控制
    test_device_control(client)
    
    # 测试语音处理
    test_voice_processing(client)
    
    print("\n✅ API 测试完成!")
    print("\n💡 下一步:")
    print("   1. 尝试通过 Web 界面访问: http://localhost:8000/docs")
    print("   2. 录制音频文件并通过 API 上传测试语音控制")
    print("   3. 集成到您的应用程序中")


if __name__ == "__main__":
    main() 