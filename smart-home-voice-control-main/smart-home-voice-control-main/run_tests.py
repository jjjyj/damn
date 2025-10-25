#!/usr/bin/env python3
"""
测试运行脚本

运行所有测试并提供测试报告。
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(command, description):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("❌ 错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行命令失败: {e}")
        return False


def main():
    """主函数"""
    print("🧪 智能家居语音控制系统 - 测试套件")
    print("=" * 60)
    
    # 检查 Python 环境
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 运行的测试列表
    tests = [
        {
            "command": "python tests/test_nlu.py",
            "description": "运行 NLU 模块测试",
            "required": True
        },
        {
            "command": "python examples/simple_voice_test.py",
            "description": "运行简单语音测试示例",
            "required": False
        }
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for test in tests:
        success = run_command(test["command"], test["description"])
        
        if success:
            success_count += 1
            print(f"✅ {test['description']} - 通过")
        else:
            print(f"❌ {test['description']} - 失败")
            if test["required"]:
                print("⚠️ 这是一个必需的测试，请检查错误")
    
    # 测试总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print(f"{'='*60}")
    print(f"总测试数: {total_count}")
    print(f"通过测试: {success_count}")
    print(f"失败测试: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 所有测试都通过了！")
        return 0
    else:
        print(f"\n⚠️ 有 {total_count - success_count} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 