#!/bin/bash

# FamilyBot 数据库启动脚本
# 启动 MySQL 和 Redis 服务

echo "🚀 启动 FamilyBot 数据库服务..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 docker-compose.yml 文件是否存在
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml 文件不存在"
    exit 1
fi

# 启动服务
echo "📦 正在启动 MySQL 和 Redis 容器..."
docker-compose up -d mysql redis

# 等待服务启动
echo "⏳ 等待数据库服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 检查 MySQL 连接
echo "🗄️ 检查 MySQL 连接..."
until docker-compose exec mysql mysqladmin ping -h"localhost" --silent; do
    echo "等待 MySQL 启动..."
    sleep 2
done
echo "✅ MySQL 已启动"

# 检查 Redis 连接
echo "📊 检查 Redis 连接..."
until docker-compose exec redis redis-cli ping | grep -q "PONG"; do
    echo "等待 Redis 启动..."
    sleep 2
done
echo "✅ Redis 已启动"

echo ""
echo "🎉 数据库服务启动完成！"
echo ""
echo "📋 服务信息:"
echo "   MySQL:     localhost:3306"
echo "   用户名:     familybot"
echo "   密码:      familybot123"
echo "   数据库:     familybot"
echo ""
echo "   Redis:     localhost:6379"
echo "   数据库:     0"
echo ""
echo "🔧 管理工具:"
echo "   phpMyAdmin:      http://localhost:8090"
echo "   Redis Commander: http://localhost:8081"
echo ""
echo "🛑 停止服务: docker-compose down"
echo "📊 查看日志: docker-compose logs -f"
