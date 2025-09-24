#!/bin/bash

echo "🛑 停止FamilyBot单端口服务..."
echo "=================================="

# 停止后端服务
echo "🏗️  停止Spring Boot服务..."
pkill -f "spring-boot:run" 2>/dev/null || true
pkill -f "familybot" 2>/dev/null || true

# 停止AI Agent
echo "🤖 停止AI Agent..."
pkill -f "uvicorn main:app" 2>/dev/null || true

# 清理PID文件
rm -f logs/ai_agent.pid logs/backend.pid 2>/dev/null || true

echo "✅ 所有服务已停止"
echo ""
echo "🌐 端口状态检查:"
lsof -i :8080 > /dev/null && echo "⚠️  端口8080仍被占用" || echo "✅ 端口8080已释放"
lsof -i :8001 > /dev/null && echo "⚠️  端口8001仍被占用" || echo "✅ 端口8001已释放"
