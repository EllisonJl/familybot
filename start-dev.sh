#!/bin/bash

# FamilyBot 开发模式快速启动
# 使用方法: ./start-dev.sh

echo "⚡ FamilyBot 开发模式启动"
echo ""

# 检查当前目录
if [ ! -f "pom.xml" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 创建日志目录
mkdir -p logs

echo "🔧 启动后端 (后台运行)..."
./mvnw spring-boot:run -Dspring-boot.run.profiles=integrated > logs/backend.log 2>&1 &
echo "   后端启动中，PID: $!"

echo "🤖 启动AI Agent (后台运行)..."
(cd ai_agent && source venv/bin/activate && python main.py > ../logs/ai_agent.log 2>&1 &)
echo "   AI Agent启动中"

echo "⏳ 等待服务初始化 (10秒)..."
sleep 10

echo "🌐 启动前端 (开发模式)..."
echo "   前端将在新终端窗口中启动"
echo "   如果前端未自动启动，请手动运行: cd frontend && npm run dev"

cd frontend
npm run dev

echo ""
echo "📍 服务地址:"
echo "   主页面: http://localhost:8080"
echo "   聊天页面: http://localhost:8080/chat"
echo ""
echo "停止服务: ./stop-all.sh"
