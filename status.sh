#!/bin/bash

# FamilyBot 状态检查脚本
# 使用方法: ./status.sh

echo "📊 FamilyBot 系统状态检查"
echo "========================="
echo ""

# 检查端口状态
check_port() {
    local port=$1
    local service=$2
    local url=$3
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo "✅ $service (端口 $port): 运行中"
        if [ ! -z "$url" ]; then
            HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null)
            if [ "$HTTP_STATUS" = "200" ]; then
                echo "   🌐 HTTP状态: 正常 ($HTTP_STATUS)"
            else
                echo "   ⚠️  HTTP状态: 异常 ($HTTP_STATUS)"
            fi
        fi
    else
        echo "❌ $service (端口 $port): 未运行"
    fi
}

# 检查所有服务
check_port 8081 "后端服务" "http://localhost:8081/api/v1/characters"
check_port 8001 "AI Agent" "http://localhost:8001/health"
check_port 8080 "前端服务" "http://localhost:8080"

echo ""
echo "🔍 进程详情："
echo "-------------"

# 检查Spring Boot进程
SPRING_PROCESS=$(ps aux | grep "spring-boot:run" | grep -v grep)
if [ ! -z "$SPRING_PROCESS" ]; then
    echo "🔧 后端进程:"
    echo "$SPRING_PROCESS" | awk '{print "   PID: " $2 ", 内存: " $4 "%, CPU: " $3 "%"}'
else
    echo "❌ 未找到后端进程"
fi

# 检查Python进程
PYTHON_PROCESS=$(ps aux | grep "python main.py" | grep -v grep)
if [ ! -z "$PYTHON_PROCESS" ]; then
    echo "🤖 AI Agent进程:"
    echo "$PYTHON_PROCESS" | awk '{print "   PID: " $2 ", 内存: " $4 "%, CPU: " $3 "%"}'
else
    echo "❌ 未找到AI Agent进程"
fi

# 检查Node.js进程
NODE_PROCESS=$(ps aux | grep "vite\|npm run dev" | grep -v grep)
if [ ! -z "$NODE_PROCESS" ]; then
    echo "🌐 前端进程:"
    echo "$NODE_PROCESS" | awk '{print "   PID: " $2 ", 内存: " $4 "%, CPU: " $3 "%"}'
else
    echo "❌ 未找到前端进程"
fi

echo ""
echo "📁 日志文件："
echo "-------------"
if [ -d "logs" ]; then
    ls -la logs/ 2>/dev/null | grep -E "\.(log)$" | awk '{print $9 ": " $5 " bytes, " $6 " " $7 " " $8}'
else
    echo "❌ 日志目录不存在"
fi

echo ""
echo "🎯 快速操作："
echo "-------------"
echo "启动系统: ./start-all.sh"
echo "停止系统: ./stop-all.sh"
echo "查看后端日志: tail -f logs/backend.log"
echo "查看AI日志: tail -f logs/ai_agent.log"
echo "查看前端日志: tail -f logs/frontend.log"

echo ""
echo "🌍 访问地址："
echo "-------------"
echo "主页面: http://localhost:8080"
echo "聊天页面: http://localhost:8080/chat"
echo "后端API: http://localhost:8081/api/v1"
echo "AI Agent API: http://localhost:8001"