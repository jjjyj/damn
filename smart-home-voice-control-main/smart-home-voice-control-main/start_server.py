#!/usr/bin/env python3
"""
服务器启动脚本

用于启动智能家居语音控制系统的 API 服务器。
"""

import sys
import os
import argparse
import uvicorn
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.smart_home.core.config import settings


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="智能家居语音控制系统 API 服务器"
    )
    
    parser.add_argument(
        "--host",
        default=settings.api_host,
        help=f"服务器地址 (默认: {settings.api_host})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.api_port,
        help=f"服务器端口 (默认: {settings.api_port})"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用自动重载 (开发模式)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="工作进程数 (默认: 1)"
    )
    
    parser.add_argument(
        "--log-level",
        default=settings.log_level.lower(),
        choices=["debug", "info", "warning", "error", "critical"],
        help=f"日志级别 (默认: {settings.log_level.lower()})"
    )
    
    return parser.parse_args()


def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查系统依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "whisper",
        "transformers",
        "torch",
        "numpy",
        "soundfile"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (缺失)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: uv sync 安装依赖")
        return False
    
    print("✅ 所有依赖检查通过")
    return True


def print_startup_info(host, port):
    """打印启动信息"""
    print(f"""
🚀 智能家居语音控制系统启动中...

📊 系统信息:
   应用名称: {settings.app_name}
   版本: {settings.version}
   Python: {sys.version.split()[0]}
   工作目录: {os.getcwd()}

🌐 服务地址:
   HTTP API: http://{host}:{port}
   API 文档: http://{host}:{port}/docs
   健康检查: http://{host}:{port}/health

🎤 支持的功能:
   ✅ 语音识别 (Whisper)
   ✅ 意图理解 (NLU)
   ✅ 设备控制 (智能灯光演示)
   ✅ RESTful API
   ✅ WebSocket 支持

💡 使用提示:
   1. 访问 API 文档了解接口详情
   2. 上传音频文件测试语音控制
   3. 查看 examples/ 目录下的示例代码

按 Ctrl+C 停止服务器
{"="*60}
""")


def main():
    """主函数"""
    args = parse_args()
    
    print("🏠 智能家居语音控制系统")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 打印启动信息
    print_startup_info(args.host, args.port)
    
    try:
        # 启动服务器
        uvicorn.run(
            "src.smart_home.api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 