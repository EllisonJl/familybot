#!/bin/bash

# FamilyBot 集成系统状态检查脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 FamilyBot集成系统状态检查${NC}"
echo "======================================="

# 检查服务状态
check_service() {
    local service_name=$1
    local port=$2
    local url=$3
    
    if lsof -i:$port >/dev/null 2>&1; then
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name 正常运行 (端口:$port)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  $service_name 端口占用但服务不响应 (端口:$port)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ $service_name 未运行 (端口:$port)${NC}"
        return 1
    fi
}

# 检查各个服务
echo -e "${BLUE}📊 服务状态:${NC}"
check_service "前端服务" 5173 "http://localhost:5173"
check_service "后端API" 8080 "http://localhost:8080/api/v1/health"
check_service "AI Agent (内部)" 8001 "http://127.0.0.1:8001"

echo ""

# 检查进程详情
echo -e "${BLUE}🔧 进程详情:${NC}"
echo "前端进程 (Vue/Vite):"
pgrep -fl "npm run dev\|vite" || echo "   未找到前端进程"

echo ""
echo "后端进程 (Spring Boot):"
pgrep -fl "spring-boot:run\|java.*familybot" || echo "   未找到后端进程"

echo ""
echo "AI Agent进程 (Python):"
pgrep -fl "uvicorn main:app" || echo "   未找到AI Agent进程"

echo ""

# 系统架构图
echo -e "${BLUE}🏗️  系统架构:${NC}"
echo "┌─────────────┐    ┌──────────────┐    ┌─────────────┐"
echo "│   前端      │◄──►│    后端      │◄──►│ AI Agent    │"
echo "│ (Vue :5173) │    │(Spring :8080)│    │(Python:8001)│"
echo "│   对外访问   │    │   统一API    │    │   内部服务   │"
echo "└─────────────┘    └──────────────┘    └─────────────┘"

echo ""

# API端点测试
echo -e "${BLUE}🌐 API端点测试:${NC}"

# 测试后端健康检查
if curl -s http://localhost:8080/api/v1/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端健康检查: http://localhost:8080/api/v1/health${NC}"
else
    echo -e "${RED}❌ 后端健康检查失败${NC}"
fi

# 测试角色列表API
if curl -s http://localhost:8080/api/v1/characters >/dev/null 2>&1; then
    echo -e "${GREEN}✅ 角色列表API: http://localhost:8080/api/v1/characters${NC}"
else
    echo -e "${RED}❌ 角色列表API失败${NC}"
fi

# 测试AI Agent (内部)
if curl -s http://127.0.0.1:8001 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ AI Agent (内部): http://127.0.0.1:8001${NC}"
else
    echo -e "${RED}❌ AI Agent (内部) 不可达${NC}"
fi

echo ""

# 访问指南
echo -e "${BLUE}📋 访问指南:${NC}"
echo "🌐 用户访问: http://localhost:5173"
echo "🔧 API文档:  http://localhost:8080/swagger-ui.html (如果启用)"
echo "📊 后端健康: http://localhost:8080/api/v1/health"

echo ""

# 日志查看提示
echo -e "${BLUE}📋 快速命令:${NC}"
echo "查看前端日志: tail -f logs/frontend.log"
echo "查看后端日志: tail -f logs/backend.log"  
echo "查看AI日志:   tail -f logs/ai_agent.log"
echo "停止所有服务: ./stop-integrated.sh"
echo "重启系统:     ./stop-integrated.sh && ./start-integrated.sh"

echo ""
echo -e "${GREEN}🏠 FamilyBot - 为留守老人提供智能陪伴服务${NC}"
