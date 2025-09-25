# 🧪 测试文件目录

这个目录包含了FamilyBot项目的所有测试脚本和测试用例。

## 🤖 AI Agent 测试

| 测试文件 | 功能描述 | 测试内容 |
|---------|----------|----------|
| `test_ai_agent.py` | AI Agent基础功能测试 | 基本对话、响应质量 |
| `test_new_agent.py` | 新版AI Agent测试 | 最新功能验证 |
| `test_cot_system.py` | Chain of Thought系统测试 | 推理链、逻辑分析 |

## 🎤 语音识别(ASR)测试

| 测试文件 | 功能描述 | 测试内容 |
|---------|----------|----------|
| `test_asr_complete.py` | 完整ASR流程测试 | 端到端语音处理 |
| `test_asr_final.py` | ASR最终版本测试 | 优化后的识别精度 |
| `test_asr_fixed.py` | ASR问题修复测试 | Bug修复验证 |
| `test_asr_json.py` | ASR JSON输出测试 | 数据格式验证 |
| `test_asr_routing.py` | ASR路由测试 | 语音指令分发 |
| `test_real_asr.py` | 真实环境ASR测试 | 实际使用场景 |

## 🗣️ 语音交互测试

| 测试文件 | 功能描述 | 测试内容 |
|---------|----------|----------|
| `test_voice_ai.py` | 语音AI交互测试 | 语音对话完整流程 |
| `test_multiple_routing.py` | 多路由测试 | 复杂对话路由 |

## 🔗 集成测试

| 测试文件 | 功能描述 | 测试内容 |
|---------|----------|----------|
| `test_integration.py` | 系统集成测试 | 各模块协同工作 |
| `test_full_system.py` | 全系统功能测试 | 端到端完整测试 |

## 🚀 运行测试

### 环境准备
```bash
# 激活AI Agent虚拟环境
cd /Users/jllulu/Desktop/familybot/ai_agent
source venv/bin/activate

# 返回测试目录
cd ../tests
```

### 运行单个测试
```bash
# 测试AI Agent基础功能
python test_ai_agent.py

# 测试语音识别
python test_asr_complete.py

# 测试完整系统
python test_full_system.py
```

### 运行所有测试
```bash
# 运行所有AI相关测试
python test_ai_agent.py && python test_new_agent.py && python test_cot_system.py

# 运行所有ASR相关测试
python test_asr_*.py

# 运行集成测试
python test_integration.py && python test_full_system.py
```

## 📝 测试注意事项

- **环境依赖**：确保AI Agent的Python虚拟环境已激活
- **音频文件**：ASR测试需要 `ai_agent/test.m4a` 音频文件
- **服务状态**：某些测试需要后端服务运行
- **API密钥**：确保相关API密钥已正确配置
- **网络连接**：部分测试需要网络访问

## 🐛 测试失败排查

1. **导入错误**：检查Python路径和依赖安装
2. **API错误**：验证密钥配置和网络连接
3. **文件缺失**：确认音频测试文件存在
4. **服务未启动**：检查必要的后端服务状态
