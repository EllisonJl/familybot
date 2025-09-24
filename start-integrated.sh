#!/bin/bash

# FamilyBot 集成启动脚本
# AI Agent作为内部服务，只有后端对外提供API

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志目录
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo -e "${BLUE}🚀 启动FamilyBot集成系统...${NC}"
echo "=================================="

# 清理旧进程
echo -e "${YELLOW}🧹 清理旧进程...${NC}"
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "spring-boot:run" 2>/dev/null || true  
pkill -f "npm run dev" 2>/dev/null || true
sleep 2

# 1. 启动AI Agent (内部服务)
echo -e "${BLUE}🤖 启动AI Agent (内部服务)...${NC}"
cd ai_agent

# 激活Python环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r ../requirements.txt
fi

# 启动AI Agent (只绑定localhost，不对外暴露)
PYTHONPATH=$PWD:$PYTHONPATH python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload &> "../$LOG_DIR/ai_agent.log" &
AI_AGENT_PID=$!
echo -e "${GREEN}✅ AI Agent已启动 (PID: $AI_AGENT_PID) - 仅内部访问${NC}"

cd ..

# 等待AI Agent启动
echo "⏳ 等待AI Agent初始化..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8001 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ AI Agent就绪${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ AI Agent启动超时${NC}"
        exit 1
    fi
    sleep 2
done

# 2. 启动后端 (对外API)
echo -e "${BLUE}🏗️  启动Spring Boot后端...${NC}"

# 确保Maven wrapper可执行
chmod +x mvnw

# 启动后端
./mvnw spring-boot:run &> "$LOG_DIR/backend.log" &
BACKEND_PID=$!
echo -e "${GREEN}✅ 后端已启动 (PID: $BACKEND_PID)${NC}"

# 等待后端启动
echo "⏳ 等待后端服务初始化..."
for i in {1..60}; do
    if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务就绪${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ 后端启动超时${NC}"
        exit 1
    fi
    sleep 3
done

# 3. 启动前端
echo -e "${BLUE}🎨 启动Vue前端...${NC}"
cd frontend

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端
npm run dev &> "../$LOG_DIR/frontend.log" &
FRONTEND_PID=$!
echo -e "${GREEN}✅ 前端已启动 (PID: $FRONTEND_PID)${NC}"

cd ..

# 等待前端启动
echo "⏳ 等待前端服务初始化..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务就绪${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 前端启动超时${NC}"
        exit 1
    fi
    sleep 2
done

# 保存PID
echo "$AI_AGENT_PID" > "$LOG_DIR/ai_agent.pid"
echo "$BACKEND_PID" > "$LOG_DIR/backend.pid" 
echo "$FRONTEND_PID" > "$LOG_DIR/frontend.pid"

echo ""
echo -e "${GREEN}🎉 FamilyBot集成系统启动成功！${NC}"
echo "=================================="
echo -e "${BLUE}🌐 访问地址:${NC}"
echo "   前端界面: http://localhost:5173"
echo "   后端API:  http://localhost:8080"
echo ""
echo -e "${YELLOW}📊 系统架构:${NC}"
echo "   前端(Vue) ←→ 后端(Spring Boot) ←→ AI Agent(内部)"
echo "   :5173          :8080              :8001(内部)"
echo ""
echo -e "${BLUE}📋 管理命令:${NC}"
echo "   查看状态: ./status-integrated.sh"
echo "   停止服务: ./stop-integrated.sh"
echo "   查看日志: tail -f logs/[service].log"
echo ""
echo -e "${GREEN}🏠 FamilyBot现在可以为留守老人提供智能陪伴服务了！${NC}"

# 保持脚本运行
wait
