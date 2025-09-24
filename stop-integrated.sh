#!/bin/bash

# FamilyBot 集成系统停止脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LOG_DIR="logs"

echo -e "${BLUE}🛑 停止FamilyBot集成系统...${NC}"
echo "=================================="

# 通过PID文件停止服务
if [ -f "$LOG_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")
    if kill "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${GREEN}✅ 前端服务已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  前端进程可能已停止${NC}"
    fi
    rm -f "$LOG_DIR/frontend.pid"
fi

if [ -f "$LOG_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$LOG_DIR/backend.pid")
    if kill "$BACKEND_PID" 2>/dev/null; then
        echo -e "${GREEN}✅ 后端服务已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  后端进程可能已停止${NC}"
    fi
    rm -f "$LOG_DIR/backend.pid"
fi

if [ -f "$LOG_DIR/ai_agent.pid" ]; then
    AI_AGENT_PID=$(cat "$LOG_DIR/ai_agent.pid")
    if kill "$AI_AGENT_PID" 2>/dev/null; then
        echo -e "${GREEN}✅ AI Agent已停止 (PID: $AI_AGENT_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  AI Agent进程可能已停止${NC}"
    fi
    rm -f "$LOG_DIR/ai_agent.pid"
fi

# 通过端口强制清理
echo -e "${YELLOW}🧹 清理残留进程...${NC}"

# 清理端口5173 (前端)
FRONTEND_PIDS=$(lsof -t -i:5173 2>/dev/null || true)
if [ -n "$FRONTEND_PIDS" ]; then
    kill $FRONTEND_PIDS 2>/dev/null || true
    echo -e "${GREEN}✅ 清理了前端端口5173${NC}"
fi

# 清理端口8080 (后端)
BACKEND_PIDS=$(lsof -t -i:8080 2>/dev/null || true)
if [ -n "$BACKEND_PIDS" ]; then
    kill $BACKEND_PIDS 2>/dev/null || true
    echo -e "${GREEN}✅ 清理了后端端口8080${NC}"
fi

# 清理端口8001 (AI Agent)
AI_PIDS=$(lsof -t -i:8001 2>/dev/null || true)
if [ -n "$AI_PIDS" ]; then
    kill $AI_PIDS 2>/dev/null || true
    echo -e "${GREEN}✅ 清理了AI Agent端口8001${NC}"
fi

# 清理特定进程名
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "spring-boot:run" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

echo ""
echo -e "${GREEN}🎯 FamilyBot集成系统已完全停止${NC}"
echo "=================================="

# 显示最终状态
sleep 2
echo -e "${BLUE}📊 端口状态检查:${NC}"
if ! lsof -i:5173 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ 端口5173 (前端) 已释放${NC}"
else
    echo -e "${RED}❌ 端口5173 (前端) 仍被占用${NC}"
fi

if ! lsof -i:8080 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ 端口8080 (后端) 已释放${NC}"
else
    echo -e "${RED}❌ 端口8080 (后端) 仍被占用${NC}"
fi

if ! lsof -i:8001 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ 端口8001 (AI Agent) 已释放${NC}"
else
    echo -e "${RED}❌ 端口8001 (AI Agent) 仍被占用${NC}"
fi
