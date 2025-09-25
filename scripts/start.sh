#!/bin/bash

# 创建日志目录
mkdir -p logs

echo "🚀 Starting FamilyBot services..."
echo "=================================="

# 检查端口是否被占用
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo "⚠️  Port $port is already in use. Stopping existing process..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# 检查必要的端口
check_port 8001 "AI Agent"
check_port 8080 "Backend" 
check_port 5173 "Frontend"

# 启动 AI Agent (Python FastAPI)
echo "🤖 Starting AI Agent..."
cd ai_agent
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r ../requirements.txt

# 启动AI Agent
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &> ../logs/ai_agent.log &
AI_AGENT_PID=$!
echo "✅ AI Agent started with PID: $AI_AGENT_PID"
cd ..

# 等待AI Agent启动
sleep 5

# 启动 Backend (Spring Boot)
echo "🏗️  Starting Backend..."
if [ ! -f "mvnw" ]; then
    echo "❌ Maven wrapper not found!"
    exit 1
fi

./mvnw spring-boot:run &> logs/backend.log &
BACKEND_PID=$!
echo "✅ Backend started with PID: $BACKEND_PID"

# 等待Backend启动
sleep 10

# 启动 Frontend (Vue)
echo "🎨 Starting Frontend..."
cd frontend

# 检查并安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

npm run dev &> ../logs/frontend.log &
FRONTEND_PID=$!
echo "✅ Frontend started with PID: $FRONTEND_PID"
cd ..

# 保存PID到文件
echo "AI Agent PID: $AI_AGENT_PID" > pids.txt
echo "Backend PID: $BACKEND_PID" >> pids.txt
echo "Frontend PID: $FRONTEND_PID" >> pids.txt

echo ""
echo "🎉 All services started successfully!"
echo "=================================="
echo "🌐 Frontend:   http://localhost:5173"
echo "🔗 Backend:    http://localhost:8080"
echo "🤖 AI Agent:   http://localhost:8001"
echo ""
echo "📊 Check logs in the 'logs' directory for service details"
echo "🛑 Use './stop.sh' to stop all services"

# 等待一下并检查服务状态
sleep 5
echo ""
echo "🔍 Checking service status..."
./status.sh