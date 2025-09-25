# 🚀 FamilyBot 启动指南

## 📋 系统架构

FamilyBot 由三个主要组件组成：

| 组件 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| 前端 | Vue.js + Vite | 8080 | 用户界面，聊天交互 |
| 后端 | Spring Boot | 8081 | API服务，数据管理 |
| AI Agent | Python FastAPI | 5000 | AI对话，语音处理 |

## ⚡ 快速启动（推荐）

### 方式一：一键启动脚本
```bash
# 启动所有服务
./start-all.sh

# 检查服务状态
./status.sh

# 停止所有服务
./stop-all.sh
```

### 方式二：开发模式
```bash
# 后台启动后端和AI，前台启动前端
./start-dev.sh
```

## 🔧 手动启动（分步骤）

### 1️⃣ 启动后端服务
```bash
# 在项目根目录
./mvnw spring-boot:run -Dspring-boot.run.profiles=integrated

# 或后台运行
./mvnw spring-boot:run -Dspring-boot.run.profiles=integrated > logs/backend.log 2>&1 &
```

### 2️⃣ 启动AI Agent
```bash
# 进入AI目录
cd ai_agent

# 激活虚拟环境
source venv/bin/activate

# 启动AI服务
python main.py

# 或后台运行
python main.py > ../logs/ai_agent.log 2>&1 &
```

### 3️⃣ 启动前端服务
```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

## 🌍 访问地址

- **主页面**: http://localhost:8080
- **聊天页面**: http://localhost:8080/chat
- **后端API**: http://localhost:8081/api/v1
- **AI Agent API**: http://localhost:5000

## 📊 服务状态检查

### 快速检查
```bash
./status.sh
```

### 手动检查
```bash
# 检查端口占用
lsof -i :8080  # 前端
lsof -i :8081  # 后端
lsof -i :5000  # AI Agent

# 检查HTTP状态
curl http://localhost:8080        # 前端
curl http://localhost:8081/api/v1/characters  # 后端
curl http://localhost:5000/health # AI Agent
```

## 📝 日志查看

```bash
# 实时查看日志
tail -f logs/backend.log    # 后端日志
tail -f logs/ai_agent.log   # AI Agent日志
tail -f logs/frontend.log   # 前端日志（如果后台运行）

# 查看所有日志文件
ls -la logs/
```

## 🛠️ 常见问题解决

### 端口被占用
```bash
# 查找占用进程
lsof -i :8080

# 终止进程
kill -9 <PID>

# 或使用脚本清理
./stop-all.sh
```

### Maven编译错误
```bash
# 清理重新编译
./mvnw clean compile

# 跳过测试编译
./mvnw clean compile -DskipTests
```

### Python环境问题
```bash
# 重建虚拟环境
cd ai_agent
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 前端依赖问题
```bash
# 清理重装依赖
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🚀 生产环境部署

### 前端构建
```bash
cd frontend
npm run build
```

### 后端打包
```bash
./mvnw clean package -DskipTests
```

### AI Agent生产运行
```bash
cd ai_agent
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 5000
```

## 🎯 功能特性

- ✅ **语音识别** (ASR): 实时语音转文字
- ✅ **语音合成** (TTS): AI回复语音播放
- ✅ **多角色对话**: 喜羊羊、美羊羊、懒羊羊
- ✅ **会话管理**: ChatGPT风格的历史对话
- ✅ **实时交互**: WebSocket长连接
- ✅ **响应式设计**: 支持桌面和移动设备

## 📞 技术支持

如果遇到问题，请：
1. 运行 `./status.sh` 检查服务状态
2. 查看相关日志文件
3. 检查端口占用情况
4. 重启相关服务

---

**享受与FamilyBot的温馨对话时光！** 🏠💝