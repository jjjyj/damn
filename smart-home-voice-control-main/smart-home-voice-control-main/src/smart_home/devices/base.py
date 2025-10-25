"""
智能设备基类定义
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime

from ..core.models import DeviceInfo, DeviceCommand, DeviceResponse, DeviceType, DeviceAction

logger = logging.getLogger(__name__)


class SmartDevice(ABC):
    """智能设备基类"""
    
    def __init__(
        self, 
        device_id: str, 
        name: str, 
        device_type: DeviceType, 
        room: str,
        brand: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化智能设备
        
        Args:
            device_id: 设备唯一标识
            name: 设备名称
            device_type: 设备类型
            room: 设备所在房间
            brand: 设备品牌
            model: 设备型号
        """
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.room = room
        self.brand = brand
        self.model = model
        self.status = {}
        self.is_online = True
        self.last_update = datetime.now()
        
        logger.info(f"初始化设备: {name} ({device_type}) - {room}")
    
    @abstractmethod
    async def execute_command(self, command: DeviceCommand) -> DeviceResponse:
        """
        执行设备命令 (抽象方法)
        
        这是一个抽象方法，需要在具体的设备子类中实现。
        例如：
        - LightDevice.execute_command() - 控制灯光开关、亮度、颜色等
        - ThermostatDevice.execute_command() - 控制温度、模式等
        - SecurityDevice.execute_command() - 控制安防设备等
        
        Args:
            command: 设备命令，包含要执行的动作和参数
            
        Returns:
            DeviceResponse: 执行结果，包含成功状态和响应数据
            
        Raises:
            NotImplementedError: 如果子类没有实现此方法
        """
        # raise NotImplementedError(f"子类 {self.__class__.__name__} 必须实现 execute_command 方法")
    
    @abstractmethod
    def get_supported_actions(self) -> list[DeviceAction]:
        """
        获取设备支持的动作列表 (抽象方法)
        
        Returns:
            支持的动作列表
        """
        pass
    
    def get_info(self) -> DeviceInfo:
        """获取设备信息"""
        return DeviceInfo(
            device_id=self.device_id,
            name=self.name,
            device_type=self.device_type,
            room=self.room,
            brand=self.brand,
            model=self.model,
            status=self.status,
            is_online=self.is_online,
            last_update=self.last_update
        )
    
    def update_status(self, status: Dict[str, Any]) -> None:
        """更新设备状态"""
        self.status.update(status)
        self.last_update = datetime.now()
        logger.debug(f"设备 {self.name} 状态更新: {status}")
    
    def set_online(self, online: bool) -> None:
        """设置设备在线状态"""
        self.is_online = online
        self.last_update = datetime.now()
        logger.info(f"设备 {self.name} {'上线' if online else '离线'}")
    
    async def turn_on(self) -> DeviceResponse:
        """打开设备"""
        command = DeviceCommand(
            device_id=self.device_id,
            action=DeviceAction.TURN_ON
        )
        return await self.execute_command(command)
    
    async def turn_off(self) -> DeviceResponse:
        """关闭设备"""
        command = DeviceCommand(
            device_id=self.device_id,
            action=DeviceAction.TURN_OFF
        )
        return await self.execute_command(command)


class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        """初始化设备管理器"""
        self.devices: Dict[str, SmartDevice] = {}
        logger.info("设备管理器初始化完成")
    
    def register_device(self, device: SmartDevice) -> None:
        """注册设备"""
        self.devices[device.device_id] = device
        logger.info(f"设备注册成功: {device.name} ({device.device_id})")
    
    def unregister_device(self, device_id: str) -> None:
        """注销设备"""
        if device_id in self.devices:
            device_name = self.devices[device_id].name
            del self.devices[device_id]
            logger.info(f"设备注销成功: {device_name} ({device_id})")
    
    def get_device(self, device_id: str) -> Optional[SmartDevice]:
        """根据设备ID获取设备"""
        return self.devices.get(device_id)
    
    def get_devices_by_room(self, room: str) -> list[SmartDevice]:
        """根据房间获取设备列表"""
        return [device for device in self.devices.values() if device.room == room]
    
    def get_devices_by_type(self, device_type: DeviceType) -> list[SmartDevice]:
        """根据设备类型获取设备列表"""
        return [device for device in self.devices.values() if device.device_type == device_type]
    
    def get_all_devices(self) -> list[SmartDevice]:
        """获取所有设备"""
        return list(self.devices.values())
    
    async def execute_command(self, command: DeviceCommand) -> DeviceResponse:
        """执行设备命令"""
        device = self.get_device(command.device_id)
        if not device:
            return DeviceResponse(
                device_id=command.device_id,
                success=False,
                message=f"设备 {command.device_id} 未找到"
            )
        
        if not device.is_online:
            return DeviceResponse(
                device_id=command.device_id,
                success=False,
                message=f"设备 {device.name} 离线"
            )
        
        try:
            return await device.execute_command(command)
        except Exception as e:
            logger.error(f"设备命令执行失败: {e}")
            return DeviceResponse(
                device_id=command.device_id,
                success=False,
                message=f"命令执行失败: {str(e)}"
            )
    
    def find_devices(
        self, 
        room: Optional[str] = None, 
        device_type: Optional[DeviceType] = None,
        name_pattern: Optional[str] = None
    ) -> list[SmartDevice]:
        """
        根据条件查找设备
        
        Args:
            room: 房间名称
            device_type: 设备类型
            name_pattern: 名称模式
            
        Returns:
            匹配的设备列表
        """
        devices = self.get_all_devices()
        
        if room:
            devices = [d for d in devices if d.room == room]
        
        if device_type:
            devices = [d for d in devices if d.device_type == device_type]
        
        if name_pattern:
            devices = [d for d in devices if name_pattern in d.name]
        
        return devices


# 全局设备管理器实例
device_manager = DeviceManager() 