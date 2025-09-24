#!/bin/bash

echo "🚀 启动FamilyBot单端口服务..."
echo "=================================="

# 创建日志目录
mkdir -p logs

# 1. 启动AI Agent (内部服务)
echo "🤖 启动AI Agent (内部服务)..."
cd ai_agent
source venv/bin/activate
PYTHONPATH=$PWD:$PYTHONPATH python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload &
AI_PID=$!
echo "✅ AI Agent已启动 (PID: $AI_PID)"
cd ..

# 等待AI Agent启动
sleep 5

# 2. 启动Spring Boot服务 (包含前端)
echo "🏗️  启动Spring Boot服务 (包含前端)..."
./mvnw spring-boot:run &
BACKEND_PID=$!
echo "✅ Spring Boot已启动 (PID: $BACKEND_PID)"

echo ""
echo "🎉 FamilyBot单端口服务配置完成！"
echo "=================================="
echo "🌐 访问地址: http://localhost:8080"
echo "📊 架构:"
echo "   用户 → Spring Boot:8080 → AI Agent:8001(内部)"
echo ""
echo "⏳ 正在启动服务，请稍等30秒后访问..."
echo ""

# 保存PID
echo $AI_PID > logs/ai_agent.pid
echo $BACKEND_PID > logs/backend.pid

# 等待服务启动完成
sleep 30
curl -s http://localhost:8080 > /dev/null && echo "🎊 服务就绪！请访问: http://localhost:8080" || echo "🔄 服务还在启动中，请稍等..."
