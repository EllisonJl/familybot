#!/bin/bash

# FamilyBot 启动脚本
# 用于快速启动所有服务

echo "🚀 启动 FamilyBot 系统..."

# 检查依赖
check_dependencies() {
    echo "📋 检查系统依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 未安装，请先安装Python 3.9+"
        exit 1
    fi
    
    # 检查Java
    if ! command -v java &> /dev/null; then
        echo "❌ Java 未安装，请先安装Java 17+"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装Node.js 16+"
        exit 1
    fi
    
    echo "✅ 系统依赖检查完成"
}

# 启动AI Agent服务
start_ai_agent() {
    echo "🤖 启动AI Agent服务..."
    
    cd ai_agent
    
    # 检查虚拟环境
    if [ ! -d "../venv" ]; then
        echo "📦 创建Python虚拟环境..."
        cd ..
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ai_agent
    else
        source ../venv/bin/activate
    fi
    
    # 启动AI Agent（后台运行）
    nohup python -m ai_agent.main > ../logs/ai_agent.log 2>&1 &
    AI_AGENT_PID=$!
    echo $AI_AGENT_PID > ../logs/ai_agent.pid
    
    echo "✅ AI Agent服务已启动 (PID: $AI_AGENT_PID)"
    echo "📍 访问地址: http://localhost:8001"
    
    cd ..
}

# 启动后端服务
start_backend() {
    echo "🔧 启动后端服务..."
    
    cd backend
    
    # 启动Spring Boot（后台运行）
    nohup mvn spring-boot:run > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
    echo "📍 访问地址: http://localhost:8080"
    
    cd ..
}

# 启动前端服务
start_frontend() {
    echo "🎨 启动前端服务..."
    
    cd frontend
    
    # 检查依赖
    if [ ! -d "node_modules" ]; then
        echo "📦 安装前端依赖..."
        npm install
    fi
    
    # 启动前端开发服务器（后台运行）
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
    echo "📍 访问地址: http://localhost:5173"
    
    cd ..
}

# 等待服务启动
wait_for_services() {
    echo "⏳ 等待服务启动..."
    
    # 等待AI Agent启动
    echo "检查AI Agent服务..."
    for i in {1..30}; do
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo "✅ AI Agent服务就绪"
            break
        fi
        sleep 2
    done
    
    # 等待后端启动
    echo "检查后端服务..."
    for i in {1..60}; do
        if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
            echo "✅ 后端服务就绪"
            break
        fi
        sleep 2
    done
    
    # 等待前端启动
    echo "检查前端服务..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo "✅ 前端服务就绪"
            break
        fi
        sleep 2
    done
}

# 显示服务状态
show_status() {
    echo ""
    echo "🎉 FamilyBot 系统启动完成！"
    echo "================================"
    echo "📱 前端地址: http://localhost:5173"
    echo "🔧 后端地址: http://localhost:8080"
    echo "🤖 AI Agent: http://localhost:8001"
    echo "📊 H2数据库: http://localhost:8080/h2-console"
    echo "================================"
    echo ""
    echo "📋 服务状态:"
    echo "- AI Agent PID: $(cat logs/ai_agent.pid 2>/dev/null || echo '未知')"
    echo "- 后端 PID: $(cat logs/backend.pid 2>/dev/null || echo '未知')"
    echo "- 前端 PID: $(cat logs/frontend.pid 2>/dev/null || echo '未知')"
    echo ""
    echo "📝 日志文件:"
    echo "- logs/ai_agent.log"
    echo "- logs/backend.log"
    echo "- logs/frontend.log"
    echo ""
    echo "⏹️  停止服务: ./stop.sh"
    echo "📊 查看状态: ./status.sh"
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p logs
    
    # 检查依赖
    check_dependencies
    
    # 启动服务
    start_ai_agent
    sleep 5
    
    start_backend
    sleep 10
    
    start_frontend
    sleep 5
    
    # 等待服务就绪
    wait_for_services
    
    # 显示状态
    show_status
}

# 捕获Ctrl+C信号
trap 'echo ""; echo "❌ 启动被中断"; exit 1' INT

# 执行主函数
main
