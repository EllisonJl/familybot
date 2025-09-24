#!/bin/bash

echo "🔍 Checking FamilyBot services status..."
echo "======================================="

check_service() {
    local port=$1
    local service_name=$2
    local endpoint=$3
    
    # 检查端口是否在监听
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ $service_name is running on port $port"
        
        # 如果提供了endpoint，测试HTTP连接
        if [ -n "$endpoint" ]; then
            if curl -s --max-time 5 "$endpoint" >/dev/null 2>&1; then
                echo "   🌐 HTTP endpoint responding: $endpoint"
            else
                echo "   ⚠️  Port open but HTTP not responding: $endpoint"
            fi
        fi
    else
        echo "❌ $service_name is NOT running on port $port"
    fi
}

# 检查各个服务
check_service 8001 "AI Agent (FastAPI)" "http://localhost:8001/"
check_service 8080 "Backend (Spring Boot)" "http://localhost:8080/api/v1/characters"
check_service 5173 "Frontend (Vue/Vite)" "http://localhost:5173/"

echo ""
echo "📊 Process details:"
echo "==================="

# 显示相关进程
echo "🤖 AI Agent processes:"
ps aux | grep -E "(uvicorn|main:app)" | grep -v grep || echo "   No AI Agent processes found"

echo ""
echo "🏗️  Backend processes:"
ps aux | grep -E "(spring-boot|mvnw)" | grep -v grep || echo "   No Backend processes found"

echo ""
echo "🎨 Frontend processes:"
ps aux | grep -E "(vite|npm.*dev)" | grep -v grep || echo "   No Frontend processes found"

echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "Frontend:  http://localhost:5173"
echo "Backend:   http://localhost:8080" 
echo "AI Agent:  http://localhost:8001"
echo "Backend API Test: http://localhost:8080/api/v1/characters"

echo ""
echo "📋 Quick commands:"
echo "=================="
echo "Start all:  ./start.sh"
echo "Stop all:   ./stop.sh"
echo "Check logs: tail -f logs/[ai_agent|backend|frontend].log"