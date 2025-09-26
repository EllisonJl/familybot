#!/bin/bash

# FamilyBot 停止脚本
# 使用方法: ./stop-all.sh

# 获取脚本目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 停止 FamilyBot 所有服务..."
echo ""

# 读取并终止保存的进程
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm -f .backend_pid
fi

if [ -f .ai_agent_pid ]; then
    AI_AGENT_PID=$(cat .ai_agent_pid)
    if kill -0 $AI_AGENT_PID 2>/dev/null; then
        echo "🤖 停止AI Agent (PID: $AI_AGENT_PID)..."
        kill $AI_AGENT_PID
    fi
    rm -f .ai_agent_pid
fi

if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🌐 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm -f .frontend_pid
fi

# 强制终止可能残留的进程
echo "🧹 清理残留进程..."
pkill -f "spring-boot:run" >/dev/null 2>&1
pkill -f "python main.py" >/dev/null 2>&1
pkill -f "vite" >/dev/null 2>&1
pkill -f "npm run dev" >/dev/null 2>&1

# 清理端口
lsof -ti :8080 | xargs kill -9 >/dev/null 2>&1
lsof -ti :8081 | xargs kill -9 >/dev/null 2>&1
lsof -ti :8001 | xargs kill -9 >/dev/null 2>&1

echo ""
echo "✅ 所有服务已停止！"
echo ""
echo "📊 可选操作："
echo "   查看日志: ls -la logs/"
echo "   清理日志: rm -rf logs/*"
echo "   重新启动: ./start-all.sh"
