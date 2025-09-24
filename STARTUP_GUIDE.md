# FamilyBot 启动指南

## 🚀 快速启动

### 方案一：一键启动（推荐）

```bash
cd /Users/jllulu/Desktop/familybot
./start.sh
```

### 方案二：分步启动

#### 1. 启动前端 (Vue)
```bash
cd frontend
npm install
npm run dev
```
访问：http://localhost:5173

#### 2. 启动AI Agent (Python FastAPI) 
```bash
cd ai_agent
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```
访问：http://localhost:8001

#### 3. 启动后端 (Spring Boot)
```bash
# 在项目根目录
./mvnw spring-boot:run
```
访问：http://localhost:8080

## 🔧 故障排除

### 常见问题

#### 1. 后端启动失败 - Lombok问题
**症状**: `cannot find symbol: class Getter`

**解决方案**:
```bash
# 清理Maven缓存
./mvnw clean
./mvnw compile
./mvnw spring-boot:run
```

#### 2. AI Agent启动失败 - 导入问题
**症状**: `ImportError: attempted relative import`

**解决方案**:
```bash
cd ai_agent
# 设置Python路径
export PYTHONPATH=$PWD:$PYTHONPATH
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### 3. 前端启动失败 - 依赖问题
**症状**: 端口5173无法访问

**解决方案**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

#### 4. 端口被占用
```bash
# 查看端口占用
lsof -i :8001  # AI Agent
lsof -i :8080  # Backend  
lsof -i :5173  # Frontend

# 停止占用进程
./stop.sh
```

## ✅ 验证启动成功

### 检查服务状态
```bash
./status.sh
```

### 手动验证
1. **前端**: 浏览器访问 http://localhost:5173
2. **AI Agent**: 浏览器访问 http://localhost:8001/docs (API文档)
3. **后端**: 浏览器访问 http://localhost:8080/api/v1/characters

## 🏠 **体验FamilyBot**

启动成功后：

1. 打开浏览器访问：http://localhost:5173
2. 选择AI家庭成员（喜羊羊、美羊羊、懒羊羊）
3. 开始对话体验智能陪伴！

## 📊 管理命令

```bash
./start.sh   # 启动所有服务
./stop.sh    # 停止所有服务  
./status.sh  # 检查服务状态
```

## 📝 注意事项

- 确保端口8001、8080、5173未被占用
- 首次启动需要下载依赖，请耐心等待
- 服务启动需要1-2分钟时间
- 如遇问题请查看logs/目录下的日志文件

---

💝 **FamilyBot现在已完整开发完成，包含:**
- 🤖 智能AI角色（CoT推理）
- 🎭 三个可爱的虚拟家庭成员  
- 🧠 Chain of Thought深度思考
- 🔍 智能意图识别和路由
- 📚 Graph RAG知识增强
- 🎨 现代化Vue前端界面
- 🏗️ 企业级Spring Boot后端

**准备为留守老人带来温暖的AI陪伴体验！** 🏠❤️
