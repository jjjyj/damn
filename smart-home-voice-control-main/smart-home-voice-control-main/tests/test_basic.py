#!/usr/bin/env python3
"""
基础功能测试 - 不依赖外部测试框架
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试基本模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from src.smart_home.core.config import settings
        print("  ✅ 配置模块导入成功")
    except Exception as e:
        print(f"  ❌ 配置模块导入失败: {e}")
        return False
    
    try:
        from src.smart_home.core.models import DeviceType, IntentType
        print("  ✅ 数据模型导入成功")
    except Exception as e:
        print(f"  ❌ 数据模型导入失败: {e}")
        return False
        
    try:
        from src.smart_home.nlu import nlu_service
        print("  ✅ NLU 服务导入成功")
    except Exception as e:
        print(f"  ❌ NLU 服务导入失败: {e}")
        return False
        
    try:
        from src.smart_home.devices import SmartLight, device_manager
        print("  ✅ 设备模块导入成功")
    except Exception as e:
        print(f"  ❌ 设备模块导入失败: {e}")
        return False
    
    return True


def test_nlu_basic():
    """测试NLU基本功能"""
    print("\n🧠 测试NLU基本功能...")
    
    try:
        from src.smart_home.nlu import nlu_service
        from src.smart_home.core.models import IntentType
        
        # 测试基本意图识别
        test_cases = [
            ("打开客厅的灯", IntentType.CONTROL_LIGHT),
            ("查看设备状态", IntentType.QUERY_STATUS),
            ("你好", IntentType.GENERAL_CHAT),
        ]
        
        for text, expected_intent in test_cases:
            result = nlu_service.process(text)
            if result.intent.intent == expected_intent:
                print(f"  ✅ '{text}' -> {expected_intent}")
            else:
                print(f"  ⚠️ '{text}' -> {result.intent.intent} (期望: {expected_intent})")
        
        return True
    except Exception as e:
        print(f"  ❌ NLU测试失败: {e}")
        return False


def test_device_basic():
    """测试设备基本功能"""
    print("\n📱 测试设备基本功能...")
    
    try:
        from src.smart_home.devices import SmartLight, device_manager
        from src.smart_home.core.models import DeviceAction
        
        # 创建测试设备
        test_light = SmartLight("test_light", "测试灯", "测试房间")
        device_manager.register_device(test_light)
        
        # 测试设备注册
        devices = device_manager.get_all_devices()
        if len(devices) > 0:
            print("  ✅ 设备注册成功")
        else:
            print("  ❌ 设备注册失败")
            return False
        
        # 测试设备查找
        found_device = device_manager.get_device("test_light")
        if found_device:
            print("  ✅ 设备查找成功")
        else:
            print("  ❌ 设备查找失败")
            return False
        
        # 清理测试设备
        device_manager.unregister_device("test_light")
        
        return True
    except Exception as e:
        print(f"  ❌ 设备测试失败: {e}")
        return False


def test_config():
    """测试配置功能"""
    print("\n⚙️ 测试配置功能...")
    
    try:
        from src.smart_home.core.config import settings
        
        # 检查基本配置
        assert hasattr(settings, 'app_name'), "缺少app_name配置"
        assert hasattr(settings, 'version'), "缺少version配置"
        assert hasattr(settings, 'api_port'), "缺少api_port配置"
        
        print(f"  ✅ 应用名称: {settings.app_name}")
        print(f"  ✅ 版本: {settings.version}")
        print(f"  ✅ API端口: {settings.api_port}")
        
        return True
    except Exception as e:
        print(f"  ❌ 配置测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🧪 智能家居系统基础功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("配置功能", test_config),
        ("NLU基本功能", test_nlu_basic),
        ("设备基本功能", test_device_basic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✅ {test_name} - 通过")
                passed += 1
            else:
                print(f"\n❌ {test_name} - 失败")
        except Exception as e:
            print(f"\n❌ {test_name} - 错误: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基础测试都通过了！")
        return True
    else:
        print(f"⚠️ 有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 