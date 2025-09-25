#!/bin/bash

echo "🛑 Stopping FamilyBot services..."
echo "================================="

stop_service_by_port() {
    local port=$1
    local service_name=$2
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "🔸 Stopping $service_name (port $port)..."
        echo "$pids" | xargs kill -TERM 2>/dev/null
        sleep 3
        
        # 如果进程仍在运行，强制终止
        local remaining_pids=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            echo "🔹 Force killing $service_name..."
            echo "$remaining_pids" | xargs kill -9 2>/dev/null
        fi
        
        # 验证是否已停止
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "✅ $service_name stopped successfully"
        else
            echo "❌ Failed to stop $service_name"
        fi
    else
        echo "ℹ️  $service_name (port $port) is not running"
    fi
}

# 如果有PID文件，按照记录的PID停止
if [ -f pids.txt ]; then
    echo "📄 Found pids.txt, stopping services by recorded PIDs..."
    while IFS= read -r line; do
        PID=$(echo $line | awk '{print $NF}')
        SERVICE_NAME=$(echo $line | awk '{print $1}')
        if [ -n "$PID" ]; then
            echo "🔸 Stopping $SERVICE_NAME with PID $PID..."
            kill $PID 2>/dev/null
            sleep 2
            
            # 检查进程是否仍在运行
            if kill -0 $PID 2>/dev/null; then
                echo "🔹 Force killing $SERVICE_NAME (PID $PID)..."
                kill -9 $PID 2>/dev/null
            fi
            
            if ! kill -0 $PID 2>/dev/null; then
                echo "✅ $SERVICE_NAME stopped successfully"
            else
                echo "❌ Failed to stop $SERVICE_NAME"
            fi
        fi
    done < pids.txt
    rm pids.txt
    echo "🗑️  Removed pids.txt"
else
    echo "📄 No pids.txt found, stopping services by port..."
fi

# 按端口停止服务（兜底机制）
stop_service_by_port 5173 "Frontend (Vue)"
stop_service_by_port 8080 "Backend (Spring Boot)"  
stop_service_by_port 8001 "AI Agent (FastAPI)"

# 清理可能的Python进程
pkill -f "uvicorn.*main:app" 2>/dev/null && echo "🔸 Cleaned up uvicorn processes"
pkill -f "spring-boot:run" 2>/dev/null && echo "🔸 Cleaned up Spring Boot processes"
pkill -f "vite.*dev" 2>/dev/null && echo "🔸 Cleaned up Vite dev processes"

echo ""
echo "🎯 All FamilyBot services stopped"
echo "================================="

# 最后检查状态
sleep 2
echo "🔍 Final status check:"
./status.sh