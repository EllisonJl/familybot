# FamilyBot - AI家庭陪伴系统

FamilyBot 是一款面向留守老人的语音交互陪伴系统。通过 AI 角色扮演（喜羊羊、懒羊羊、美羊羊等），老人可以和虚拟的"家人"进行自然的语音对话。系统结合多轮对话、上下文记忆、RAG 技术，让交流更真实、更贴心。

## 🌟 主要特性

### 👥 多角色AI陪伴
- **喜羊羊（儿子）**: 聪明、勇敢、孝顺，关心家人健康
- **美羊羊（女儿）**: 温柔、细心、贴心，善于倾听安慰
- **懒羊羊（孙子）**: 可爱、天真、活泼，让人开心

### 🎙️ 智能语音交互
- **语音识别（ASR）**: 基于通义千问ASR模型
- **语音合成（TTS）**: 基于通义千问TTS模型
- **多角色声音**: 每个角色都有独特的声音特征

### 🧠 智能对话管理
- **多轮对话**: 上下文感知的连续对话
- **情绪识别**: 识别用户情绪并适当回应
- **意图理解**: 理解用户真实需求
- **记忆系统**: 长期和短期记忆管理

### 🔧 可扩展架构
- **角色扩展**: 轻松添加新的AI角色
- **模型扩展**: 支持多种AI模型
- **声音扩展**: 支持不同语音配置
- **技能扩展**: 模块化技能系统

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue3)   │◄──►│ 后端 (Spring)  │◄──►│ AI层 (Python)  │
│                 │    │                 │    │                 │
│ • 聊天界面     │    │ • RESTful API  │    │ • LangGraph    │
│ • 角色选择     │    │ • 数据库管理   │    │ • 多角色Agent  │
│ • 语音交互     │    │ • 会话管理     │    │ • ASR/TTS     │
│ • 历史记录     │    │ • 用户管理     │    │ • 记忆系统     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 环境要求

- Node.js 16+
- Java 17+
- Python 3.9+
- Maven 3.6+

### 1. 克隆项目

```bash
git clone <项目地址>
cd familybot
```

### 2. 启动AI Agent服务

```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动AI Agent服务
cd ai_agent
python -m ai_agent.main
```

AI Agent服务将在 http://localhost:8001 启动

### 3. 启动后端服务

```bash
# 启动Spring Boot后端
cd backend
mvn spring-boot:run
```

后端服务将在 http://localhost:8080 启动

### 4. 启动前端服务

```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

### 5. 访问应用

打开浏览器访问 http://localhost:5173 即可使用FamilyBot！

## 📁 项目结构

```
familybot/
├── ai_agent/                    # AI代理服务 (Python)
│   ├── agents/                  # 角色代理
│   │   └── character_agent.py   # 角色管理
│   ├── graph/                   # LangGraph工作流
│   │   └── conversation_graph.py # 对话图
│   ├── memory/                  # 记忆系统
│   │   └── conversation_memory.py # 对话记忆
│   ├── services/                # 服务层
│   │   └── audio_service.py     # 音频服务
│   ├── config.py               # 配置管理
│   └── main.py                 # 主服务入口
├── backend/                     # 后端服务 (Spring Boot)
│   ├── src/main/java/cn/qiniu/familybot/
│   │   ├── controller/         # 控制器
│   │   ├── service/            # 服务层
│   │   ├── repository/         # 数据访问层
│   │   ├── model/              # 数据模型
│   │   ├── dto/                # 数据传输对象
│   │   └── config/             # 配置类
│   └── src/main/resources/
│       └── application.properties # 应用配置
├── frontend/                    # 前端界面 (Vue3)
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── services/           # API服务
│   │   ├── router/             # 路由配置
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 入口文件
│   ├── .env.development        # 开发环境配置
│   └── package.json            # 依赖配置
├── requirements.txt             # Python依赖
├── pom.xml                     # Maven配置
└── README.md                   # 项目说明
```

## 🔧 配置说明

### AI Agent配置

在 `ai_agent/config.py` 中配置：

```python
# API密钥
DASHSCOPE_API_KEY = "your-api-key"

# 模型配置
LLM_MODEL = "qwen3-max-preview"
TTS_MODEL = "qwen3-tts-flash"
ASR_MODEL = "qwen3-asr-flash"

# 角色配置
CHARACTER_CONFIGS = {
    "xiyang": {
        "name": "喜羊羊",
        "voice": "Cherry",
        # ... 更多配置
    }
}
```

### 后端配置

在 `backend/src/main/resources/application.properties` 中配置：

```properties
# 服务端口
server.port=8080

# 数据库配置
spring.datasource.url=jdbc:h2:mem:familybot

# AI Agent服务地址
familybot.ai-agent.base-url=http://localhost:8001
```

### 前端配置

在 `frontend/.env.development` 中配置：

```env
# API地址
VITE_API_BASE_URL=http://localhost:8080/api/v1
VITE_AI_AGENT_BASE_URL=http://localhost:8001
```

## 🎯 使用指南

### 基本对话

1. 打开应用后，系统会默认选择"喜羊羊"角色
2. 在输入框中输入消息，点击发送
3. AI会以选定角色的身份回复
4. 支持语音输入和语音播放

### 切换角色

1. 点击顶部的"切换角色"按钮
2. 在弹出的角色选择器中选择想要对话的角色
3. 每个角色都有不同的性格和对话风格

### 语音交互

- **语音输入**: 点击麦克风按钮开始录音
- **语音播放**: 点击消息旁的播放按钮听取语音回复

## 🔍 API文档

### 后端API

- **POST** `/api/v1/chat` - 发送聊天消息
- **GET** `/api/v1/characters` - 获取角色列表
- **POST** `/api/v1/characters/{id}/switch` - 切换角色
- **GET** `/api/v1/conversations` - 获取对话历史
- **GET** `/api/v1/users/{id}/stats` - 获取用户统计

### AI Agent API

- **POST** `/chat` - 文本聊天
- **POST** `/voice-chat` - 语音聊天
- **POST** `/asr` - 语音识别
- **POST** `/tts` - 语音合成
- **GET** `/characters` - 获取角色信息

## 🛠️ 开发指南

### 添加新角色

1. 在 `ai_agent/config.py` 的 `CHARACTER_CONFIGS` 中添加角色配置
2. 在数据库中添加角色记录（或通过API创建）
3. 为角色添加头像和背景图片

### 扩展新功能

1. **后端**: 在相应的Controller、Service、Repository中添加逻辑
2. **AI Agent**: 在graph或agents目录中添加新的节点或代理
3. **前端**: 在views或components中添加新的界面组件

### 集成新模型

1. 在 `ai_agent/config.py` 中添加模型配置
2. 在相应的服务类中实现模型调用逻辑
3. 更新角色配置以使用新模型

## 🚀 部署指南

### Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 生产部署

1. **前端**: 构建并部署到静态文件服务器
2. **后端**: 打包为JAR文件部署到应用服务器
3. **AI Agent**: 使用WSGI服务器（如Gunicorn）部署

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系我们

如有问题或建议，请联系：

- 项目维护者: [联系邮箱]
- 项目地址: [GitHub地址]

---

**让AI陪伴温暖每一位老人 ❤️**
