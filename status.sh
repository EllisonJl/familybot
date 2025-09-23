#!/bin/bash

# FamilyBot 状态检查脚本
# 用于查看所有服务的运行状态

echo "📊 FamilyBot 系统状态检查"
echo "=========================="

# 检查服务状态
check_service() {
    local service_name=$1
    local pid_file=$2
    local url=$3
    
    echo ""
    echo "🔍 检查 $service_name:"
    echo "------------------------"
    
    # 检查PID文件
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "✅ 进程状态: 运行中 (PID: $pid)"
        else
            echo "❌ 进程状态: 已停止 (PID文件存在但进程不存在)"
            return 1
        fi
    else
        echo "❌ 进程状态: 未启动 (PID文件不存在)"
        return 1
    fi
    
    # 检查网络连接
    if [ -n "$url" ]; then
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ 网络状态: 可访问"
            echo "📍 访问地址: $url"
        else
            echo "❌ 网络状态: 不可访问"
            echo "📍 预期地址: $url"
            return 1
        fi
    fi
    
    return 0
}

# 显示资源使用情况
show_resource_usage() {
    echo ""
    echo "💻 系统资源使用情况:"
    echo "------------------------"
    
    # CPU和内存使用情况
    echo "🖥️  CPU 使用率:"
    top -l 1 | grep "CPU usage" || echo "无法获取CPU信息"
    
    echo ""
    echo "💾 内存使用情况:"
    free -h 2>/dev/null || vm_stat | head -5
    
    echo ""
    echo "💽 磁盘使用情况:"
    df -h . | tail -1
}

# 显示最近的日志
show_recent_logs() {
    echo ""
    echo "📝 最近的服务日志:"
    echo "------------------------"
    
    for log_file in logs/*.log; do
        if [ -f "$log_file" ]; then
            echo ""
            echo "📄 $(basename "$log_file"):"
            tail -3 "$log_file" 2>/dev/null || echo "无法读取日志文件"
        fi
    done
}

# 检查端口占用
check_ports() {
    echo ""
    echo "🔌 端口使用情况:"
    echo "------------------------"
    
    local ports=(5173 8080 8001)
    local port_names=("前端" "后端" "AI Agent")
    
    for i in "${!ports[@]}"; do
        local port=${ports[$i]}
        local name=${port_names[$i]}
        
        if lsof -i :$port > /dev/null 2>&1; then
            local process=$(lsof -ti :$port | head -1)
            echo "✅ 端口 $port ($name): 已占用 (PID: $process)"
        else
            echo "❌ 端口 $port ($name): 未占用"
        fi
    done
}

# 主函数
main() {
    local all_healthy=true
    
    # 检查各个服务
    check_service "AI Agent服务" "logs/ai_agent.pid" "http://localhost:8001/health" || all_healthy=false
    check_service "后端服务" "logs/backend.pid" "http://localhost:8080/api/v1/health" || all_healthy=false
    check_service "前端服务" "logs/frontend.pid" "http://localhost:5173" || all_healthy=false
    
    # 检查端口
    check_ports
    
    # 显示资源使用情况
    show_resource_usage
    
    # 显示最近日志
    show_recent_logs
    
    # 总体状态
    echo ""
    echo "=========================="
    if $all_healthy; then
        echo "🎉 系统状态: 全部服务正常运行"
        echo "📱 前端访问: http://localhost:5173"
    else
        echo "⚠️  系统状态: 部分服务异常"
        echo "🔧 请检查上述详情并重启相关服务"
    fi
    echo "=========================="
    
    echo ""
    echo "🚀 启动服务: ./start.sh"
    echo "⏹️  停止服务: ./stop.sh"
    echo "🔄 重启服务: ./restart.sh"
}

# 执行主函数
main
