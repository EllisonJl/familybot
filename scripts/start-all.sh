#!/bin/bash

# FamilyBot 一键启动脚本
# 使用方法: ./start-all.sh

echo "🚀 启动 FamilyBot 完整系统..."
echo ""

# 创建日志目录
mkdir -p logs

# 检查端口是否被占用
check_port() {
    local port=$1
    local service=$2
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用 ($service)，正在终止现有进程..."
        lsof -ti :$port | xargs kill -9 >/dev/null 2>&1
        sleep 2
    fi
}

# 检查并清理端口
check_port 8080 "前端"
check_port 8081 "后端"  
check_port 8001 "AI Agent"

# 获取项目根目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔧 启动后端服务 (Spring Boot)..."
cd "$PROJECT_ROOT"
export MAVEN_OPTS="-Xmx1G -Xms512m"  # 内存优化配置
./mvnw spring-boot:run -Dspring-boot.run.profiles=integrated > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

echo "🤖 启动AI Agent (Python FastAPI)..."
cd "$PROJECT_ROOT/ai_agent"
source venv/bin/activate
python main.py > ../logs/ai_agent.log 2>&1 &
AI_AGENT_PID=$!
echo "   AI Agent PID: $AI_AGENT_PID"
cd "$PROJECT_ROOT"

echo "⏳ 等待后端服务启动 (15秒)..."
sleep 15

echo "🌐 启动前端开发服务器 (Vue.js)..."
cd "$PROJECT_ROOT/frontend"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"

# 保存进程ID到文件（保存到scripts目录）
cd "$SCRIPT_DIR"
echo "$BACKEND_PID" > .backend_pid
echo "$AI_AGENT_PID" > .ai_agent_pid  
echo "$FRONTEND_PID" > .frontend_pid

echo ""
echo "✅ 所有服务启动完成！"
echo ""
echo "📍 访问地址："
echo "   主页面: http://localhost:8080"
echo "   聊天页面: http://localhost:8080/chat"
echo ""
echo "📋 服务状态："
echo "   后端: http://localhost:8081 (PID: $BACKEND_PID)"
echo "   AI Agent: http://localhost:8001 (PID: $AI_AGENT_PID)"
echo "   前端: http://localhost:8080 (PID: $FRONTEND_PID)"
echo ""
echo "📊 查看日志："
echo "   tail -f logs/backend.log    # 后端日志"
echo "   tail -f logs/ai_agent.log   # AI Agent日志"
echo "   tail -f logs/frontend.log   # 前端日志"
echo ""
echo "🛑 停止服务："
echo "   ./stop-all.sh"
echo ""
echo "⏰ 等待前端编译完成，大约需要10-30秒..."
