"""
智能灯光设备实现
"""

from typing import Any, Dict
import asyncio
import logging

from .base import SmartDevice
from ..core.models import DeviceCommand, DeviceResponse, DeviceType, DeviceAction

logger = logging.getLogger(__name__)


class SmartLight(SmartDevice):
    """智能灯光设备"""
    
    def __init__(self, device_id: str, name: str, room: str, **kwargs):
        """
        初始化智能灯光
        
        Args:
            device_id: 设备ID
            name: 设备名称
            room: 所在房间
        """
        super().__init__(device_id, name, DeviceType.LIGHT, room, **kwargs)
        
        # 初始化灯光状态
        self.status = {
            "power": False,           # 电源状态
            "brightness": 100,        # 亮度 (0-100)
            "color": "#FFFFFF",       # 颜色 (十六进制)
            "color_temp": 4000,       # 色温 (K)
            "mode": "normal"          # 模式 (normal, reading, sleep, party)
        }
        
        logger.info(f"智能灯光 {name} 初始化完成")
    
    def get_supported_actions(self) -> list[DeviceAction]:
        """获取支持的动作"""
        return [
            DeviceAction.TURN_ON,
            DeviceAction.TURN_OFF,
            DeviceAction.SET_BRIGHTNESS,
            DeviceAction.SET_COLOR
        ]
    
    async def execute_command(self, command: DeviceCommand) -> DeviceResponse:
        """执行灯光控制命令"""
        try:
            action = command.action
            params = command.parameters
            
            if action == DeviceAction.TURN_ON:
                return await self._turn_on()
            elif action == DeviceAction.TURN_OFF:
                return await self._turn_off()
            elif action == DeviceAction.SET_BRIGHTNESS:
                brightness = params.get("brightness", 100)
                return await self._set_brightness(brightness)
            elif action == DeviceAction.SET_COLOR:
                color = params.get("color", "#FFFFFF")
                return await self._set_color(color)
            else:
                return DeviceResponse(
                    device_id=self.device_id,
                    success=False,
                    message=f"不支持的动作: {action}"
                )
                
        except Exception as e:
            logger.error(f"执行灯光命令失败: {e}")
            return DeviceResponse(
                device_id=self.device_id,
                success=False,
                message=f"命令执行失败: {str(e)}"
            )
    
    async def _turn_on(self) -> DeviceResponse:
        """打开灯光"""
        # 模拟网络延迟
        await asyncio.sleep(0.1)
        
        self.update_status({"power": True})
        
        return DeviceResponse(
            device_id=self.device_id,
            success=True,
            message=f"{self.name} 已打开",
            new_status=self.status.copy()
        )
    
    async def _turn_off(self) -> DeviceResponse:
        """关闭灯光"""
        # 模拟网络延迟
        await asyncio.sleep(0.1)
        
        self.update_status({"power": False})
        
        return DeviceResponse(
            device_id=self.device_id,
            success=True,
            message=f"{self.name} 已关闭",
            new_status=self.status.copy()
        )
    
    async def _set_brightness(self, brightness: int) -> DeviceResponse:
        """设置亮度"""
        # 验证亮度范围
        brightness = max(0, min(100, brightness))
        
        # 模拟网络延迟
        await asyncio.sleep(0.1)
        
        # 如果设置亮度且灯处于关闭状态，则打开灯
        if brightness > 0 and not self.status["power"]:
            self.update_status({"power": True, "brightness": brightness})
            message = f"{self.name} 已打开并设置亮度为 {brightness}%"
        else:
            self.update_status({"brightness": brightness})
            message = f"{self.name} 亮度已设置为 {brightness}%"
        
        return DeviceResponse(
            device_id=self.device_id,
            success=True,
            message=message,
            new_status=self.status.copy()
        )
    
    async def _set_color(self, color: str) -> DeviceResponse:
        """设置颜色"""
        # 颜色名称到十六进制的映射
        color_map = {
            "红色": "#FF0000", "红": "#FF0000",
            "绿色": "#00FF00", "绿": "#00FF00", 
            "蓝色": "#0000FF", "蓝": "#0000FF",
            "黄色": "#FFFF00", "黄": "#FFFF00",
            "紫色": "#FF00FF", "紫": "#FF00FF",
            "青色": "#00FFFF", "青": "#00FFFF",
            "白色": "#FFFFFF", "白": "#FFFFFF",
            "暖色": "#FFB366", "暖白": "#FFB366",
            "冷色": "#B3E5FF", "冷白": "#B3E5FF"
        }
        
        # 转换颜色名称
        if color in color_map:
            color = color_map[color]
        
        # 验证十六进制颜色格式
        if not color.startswith("#") or len(color) != 7:
            return DeviceResponse(
                device_id=self.device_id,
                success=False,
                message=f"无效的颜色格式: {color}"
            )
        
        # 模拟网络延迟
        await asyncio.sleep(0.1)
        
        # 如果设置颜色且灯处于关闭状态，则打开灯
        if not self.status["power"]:
            self.update_status({"power": True, "color": color})
            message = f"{self.name} 已打开并设置为指定颜色"
        else:
            self.update_status({"color": color})
            message = f"{self.name} 颜色已更改"
        
        return DeviceResponse(
            device_id=self.device_id,
            success=True,
            message=message,
            new_status=self.status.copy()
        ) 