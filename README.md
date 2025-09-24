# FamilyBot - AI家庭陪伴系统

<div align="center">
  <h2>🏠 专为留守老人设计的智能陪伴助手</h2>
  <p>通过AI角色扮演技术，为老年人提供温暖的虚拟家庭成员对话体验</p>
</div>

## 🌟 系统特色

### 🎭 三个可爱的虚拟家庭成员
- **喜羊羊（儿子）** - 28岁，理性稳重，专业负责，擅长健康建议和生活指导
- **美羊羊（女儿）** - 25岁，温柔体贴，善解人意，提供情感支持和贴心关怀
- **懒羊羊（孙子）** - 7岁，天真烂漫，活泼可爱，带来童趣和欢乐

### 🧠 Chain of Thought 深度思考
- **成年角色推理能力**: 喜羊羊和美羊羊具备5步深度思考流程
- **个性化分析**: 根据角色特质提供不同维度的关怀
- **专业建议**: 结合医学、心理学知识给出实用指导

### 🔍 智能意图识别
- **精准路由**: 自动识别用户意图，路由到最适合的角色
- **上下文理解**: 基于对话历史和情感状态智能响应
- **多场景支持**: 健康咨询、情感支持、知识问答、日常闲聊

### 🎙️ 多模态交互
- **语音对话**: 支持语音输入和TTS语音回复
- **文本聊天**: 流畅的文字对话体验
- **情感表达**: 根据对话内容调整回复情绪和语调

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue Frontend  │    │ Spring Backend  │    │  AI Agent       │
│   (Port 5173)   │◄──►│   (Port 8080)   │◄──►│  (Port 8001)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                      │                      │
│ • 用户界面            │ • RESTful API        │ • LangGraph工作流
│ • 角色选择            │ • 数据管理            │ • CoT推理引擎
│ • 消息展示            │ • 业务逻辑            │ • Graph RAG
│ • 语音交互            │ • 数据库操作          │ • 多角色管理
│                      │                      │ • TTS/ASR服务
```

## 🚀 快速启动

### 系统要求
- **Python 3.8+** (推荐 3.10)
- **Node.js 16+** 和 npm
- **Java 17+** 和 Maven 3.6+
- **操作系统**: macOS, Linux, Windows

### 一键启动

```bash
# 克隆项目（如果需要）
git clone <repository-url>
cd familybot

# 一键启动所有服务
./start.sh
```

### 手动启动（可选）

1. **启动 AI Agent**
```bash
cd ai_agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

2. **启动 Backend**
```bash
cd backend
./mvnw spring-boot:run
```

3. **启动 Frontend**
```bash
cd frontend
npm install
npm run dev
```

### 访问系统
- 🌐 **前端界面**: http://localhost:5173
- 🔗 **后端API**: http://localhost:8080
- 🤖 **AI服务**: http://localhost:8001

## 📱 使用指南

### 1. 选择家庭成员
- 首次进入系统会提示选择角色
- 可随时点击"切换角色"更换对话对象
- 不同角色有各自的性格特点和专长

### 2. 开始对话
- **文字聊天**: 在输入框中键入消息，按Enter发送
- **语音聊天**: 点击麦克风按钮进行语音输入（开发中）
- **查看历史**: 所有对话记录自动保存

### 3. 体验智能功能
- **健康咨询**: "我最近血压有点高，该怎么办？"
- **情感倾诉**: "我感到很孤单，没人陪我说话"
- **生活指导**: "天气变冷了，需要注意什么？"
- **童趣互动**: "小懒羊羊，给爷爷讲个故事吧！"

## 🛠️ 管理命令

```bash
# 检查服务状态
./status.sh

# 停止所有服务
./stop.sh

# 查看日志
tail -f logs/ai_agent.log     # AI服务日志
tail -f logs/backend.log      # 后端服务日志
tail -f logs/frontend.log     # 前端服务日志

# 运行系统测试
python test_full_system.py

# 运行AI Agent测试
python test_new_agent.py

# 运行CoT测试
python test_cot_system.py
```

## 🧪 测试功能

### 集成测试
```bash
# 运行完整系统测试
python test_full_system.py
```

测试覆盖：
- ✅ 服务健康检查
- ✅ API接口功能
- ✅ 服务间通信
- ✅ CoT推理功能
- ✅ 角色路由准确性

### 单元测试
```bash
# AI Agent核心功能测试
python test_new_agent.py

# CoT推理系统测试
python test_cot_system.py
```

## 📊 技术栈

### 前端 (Vue 3)
- **框架**: Vue 3 + Composition API
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **构建工具**: Vite
- **HTTP客户端**: Axios

### 后端 (Spring Boot)
- **框架**: Spring Boot 3.5.6
- **数据库**: H2 (开发) / PostgreSQL (生产)
- **ORM**: Spring Data JPA
- **API**: RESTful + JSON
- **HTTP客户端**: WebClient
- **工具**: Lombok

### AI Agent (Python)
- **Web框架**: FastAPI
- **工作流引擎**: LangGraph
- **LLM接口**: LangChain + OpenAI API
- **推理引擎**: 自研CoT处理器
- **知识增强**: Graph RAG
- **语音服务**: DashScope TTS/ASR
- **数据验证**: Pydantic

## 🔧 配置文件

### 环境变量 (.env)
```bash
# AI模型配置
DASHSCOPE_API_KEY=your_dashscope_key
OPENAI_API_KEY=your_openai_key

# 服务地址
AI_AGENT_BASE_URL=http://localhost:8001
BACKEND_BASE_URL=http://localhost:8080
```

### 自定义配置
- **AI Agent**: `ai_agent/config.py`
- **Backend**: `backend/src/main/resources/application.properties`
- **Frontend**: `frontend/vite.config.js`

## 📈 性能指标

- **响应时间**: AI回复 < 3秒，CoT推理 < 5秒
- **并发支持**: 100+ 用户同时在线
- **内存占用**: AI Agent ~500MB, Backend ~200MB
- **准确率**: 意图识别 >95%, 角色路由 >90%

## 🚨 故障排除

### 常见问题

1. **端口被占用**
```bash
# 查看端口占用
lsof -i :8001
lsof -i :8080
lsof -i :5173

# 停止相关进程
./stop.sh
```

2. **依赖安装失败**
```bash
# Python依赖
cd ai_agent && pip install -r requirements.txt

# Node.js依赖
cd frontend && npm install

# Maven依赖
cd backend && ./mvnw dependency:resolve
```

3. **API密钥配置**
- 确保 `.env` 文件包含正确的API密钥
- 检查网络连接和API服务状态

### 日志分析
```bash
# 查看错误日志
grep -i error logs/*.log

# 实时监控
tail -f logs/ai_agent.log | grep -i error
```

## 🤝 开发贡献

### 项目结构
```
familybot/
├── ai_agent/          # AI服务核心
│   ├── agents/        # 角色管理
│   ├── graph/         # LangGraph工作流
│   ├── reasoning/     # CoT推理引擎
│   ├── rag/          # Graph RAG系统
│   └── services/     # 基础服务
├── backend/          # Spring Boot后端
│   └── src/main/java/cn/qiniu/familybot/
├── frontend/         # Vue前端
│   └── src/
│       ├── components/
│       ├── views/
│       └── stores/
└── logs/            # 运行日志
```

### 开发工作流
1. Fork 项目
2. 创建功能分支
3. 本地测试验证
4. 提交Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下开源项目的支持：
- LangChain & LangGraph
- Vue.js & Element Plus
- Spring Boot
- FastAPI

---

<div align="center">
  <p>💝 用技术传递温暖，让每一位老人都有家人陪伴 💝</p>
  <p>📧 联系方式: [your-email@example.com]</p>
</div>