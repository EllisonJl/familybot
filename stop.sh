#!/bin/bash

# FamilyBot 停止脚本
# 用于停止所有服务

echo "⏹️  停止 FamilyBot 系统..."

# 停止服务
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "⏹️  停止 $service_name (PID: $pid)..."
            kill $pid
            
            # 等待进程结束
            for i in {1..10}; do
                if ! ps -p $pid > /dev/null 2>&1; then
                    echo "✅ $service_name 已停止"
                    break
                fi
                sleep 1
            done
            
            # 如果进程仍在运行，强制杀死
            if ps -p $pid > /dev/null 2>&1; then
                echo "🔥 强制停止 $service_name..."
                kill -9 $pid
            fi
        else
            echo "ℹ️  $service_name 未运行"
        fi
        rm -f "$pid_file"
    else
        echo "ℹ️  $service_name PID文件不存在"
    fi
}

# 停止所有服务
stop_all_services() {
    stop_service "前端服务" "logs/frontend.pid"
    stop_service "后端服务" "logs/backend.pid"
    stop_service "AI Agent服务" "logs/ai_agent.pid"
}

# 清理资源
cleanup() {
    echo "🧹 清理资源..."
    
    # 查找并停止可能的遗留进程
    pkill -f "mvn spring-boot:run" 2>/dev/null || true
    pkill -f "ai_agent.main" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    # 清理PID文件
    rm -f logs/*.pid
    
    echo "✅ 清理完成"
}

# 主函数
main() {
    stop_all_services
    cleanup
    
    echo ""
    echo "🎉 FamilyBot 系统已完全停止"
    echo ""
    echo "🚀 重新启动: ./start.sh"
    echo "📊 查看状态: ./status.sh"
}

# 执行主函数
main
