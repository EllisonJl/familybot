"""
FamilyBot AI Agent 入口文件
用于启动主服务或运行测试
"""

from .main import start_server
from .config import Config
from .services.audio_service import audio_service

if __name__ == "__main__":
    # 启动主服务
    start_server()
