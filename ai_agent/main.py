"""
FamilyBot AI Agent 主服务
提供FastAPI接口，集成所有AI功能模块
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Optional, Dict, Any, List
import asyncio
import os
from datetime import datetime

from config import Config
from graph.conversation_graph import ConversationGraph
from services.audio_service import audio_service


# === 数据模型 ===
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    user_id: str = "default"
    character_id: str = "xiyang"
    context: Optional[Dict[str, Any]] = None
    use_agent: Optional[bool] = True
    role: Optional[str] = "elderly"
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应模型"""
    character_id: str
    character_name: str
    response: str
    emotion: str
    timestamp: str
    voice_config: Optional[Dict[str, Any]] = None


class VoiceChatRequest(BaseModel):
    """语音聊天请求模型"""
    user_id: str = "default"
    character_id: str = "xiyang"
    context: Optional[Dict[str, Any]] = None


class VoiceChatResponse(BaseModel):
    """语音聊天响应模型"""
    character_id: str
    character_name: str
    response: str
    emotion: str
    audio_url: Optional[str] = None
    timestamp: str


class CharacterInfo(BaseModel):
    """角色信息模型"""
    id: str
    name: str
    role: str
    personality: str
    voice: str
    greeting: str


# === 初始化FastAPI应用 ===
app = FastAPI(
    title="FamilyBot AI Agent",
    description="家庭陪伴机器人AI代理服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化对话图
conversation_graph = ConversationGraph()


# === 健康检查 ===
@app.get("/")
async def root():
    """根路径接口"""
    return {
        "service": "FamilyBot AI Agent",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# === 角色管理接口 ===
@app.get("/characters", response_model=List[CharacterInfo])
async def get_characters():
    """获取所有可用角色"""
    try:
        characters = conversation_graph.get_available_characters()
        return characters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色列表失败: {str(e)}")


@app.post("/characters/{character_id}/switch")
async def switch_character(character_id: str):
    """切换当前角色"""
    try:
        success = conversation_graph.switch_character(character_id)
        if success:
            return {"message": f"已切换到角色: {character_id}"}
        else:
            raise HTTPException(status_code=404, detail=f"角色 {character_id} 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换角色失败: {str(e)}")


@app.get("/characters/{character_id}/greeting")
async def get_character_greeting(character_id: str):
    """获取角色问候语"""
    try:
        agent = conversation_graph.character_manager.get_agent(character_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"角色 {character_id} 不存在")
        
        greeting = agent.get_greeting()
        return {
            "character_id": character_id,
            "character_name": agent.config["name"],
            "greeting": greeting
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取问候语失败: {str(e)}")


# === 文本聊天接口 ===
@app.post("/chat", response_model=ChatResponse)
async def text_chat(request: ChatRequest):
    """文本聊天接口"""
    try:
        print(f"📝 收到聊天请求: {request.user_id} -> {request.character_id}: {request.message[:50]}...")
        print(f"🎯 使用Agent: {request.use_agent}, 角色: {request.role}, 线程ID: {request.thread_id}")
        
        # 直接使用角色管理器生成回复（绕过LangGraph）
        from agents.character_agent import CharacterManager
        from datetime import datetime
        
        character_manager = CharacterManager()
        agent = character_manager.get_agent(request.character_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"角色 {request.character_id} 不存在")
        
        # 生成回复
        response_data = agent.generate_response(request.message)
        
        print(f"✅ 生成回复: {response_data['character_name']} -> {response_data['response'][:50]}...")
        
        return ChatResponse(
            character_id=response_data["character_id"],
            character_name=response_data["character_name"],
            response=response_data["response"],
            emotion=response_data["emotion"],
            timestamp=response_data["timestamp"],
            voice_config=response_data.get("voice_config")
        )
        
    except Exception as e:
        print(f"❌ 聊天处理失败: {str(e)}")
        # 返回fallback回复
        try:
            from config import CHARACTER_CONFIGS
        except ImportError:
            CHARACTER_CONFIGS = {}
        
        character_config = CHARACTER_CONFIGS.get(request.character_id, {})
        return ChatResponse(
            character_id=request.character_id,
            character_name=character_config.get("name", "系统"),
            response="抱歉，我现在有点问题，请稍后再试。",
            emotion="error",
            timestamp=datetime.now().isoformat()
        )


# === 语音聊天接口 ===
@app.post("/voice-chat", response_model=VoiceChatResponse)
async def voice_chat(
    audio_file: UploadFile = File(...),
    user_id: str = "default",
    character_id: str = "xiyang"
):
    """语音聊天接口"""
    try:
        # 读取音频文件
        audio_data = await audio_file.read()
        
        # 语音识别
        asr_result = await audio_service.speech_to_text(
            audio_data=audio_data,
            source_format=audio_file.filename.split('.')[-1] if audio_file.filename else 'wav'
        )
        
        if not asr_result["success"]:
            raise HTTPException(status_code=400, detail=f"语音识别失败: {asr_result['error']}")
        
        user_text = asr_result["text"]
        if not user_text.strip():
            raise HTTPException(status_code=400, detail="未识别到有效语音内容")
        
        # 处理对话（异步）
        result = await conversation_graph.process_conversation(
            user_input=user_text,
            user_id=user_id,
            character_id=character_id
        )
        
        # 语音合成
        voice_config = result.get("voice_config", {})
        tts_audio = await audio_service.text_to_speech(
            text=result["response"],
            voice=voice_config.get("voice", "Cherry"),
            speed=voice_config.get("speed", 1.0)
        )
        
        # 这里简化处理，实际应该保存音频文件并返回URL
        audio_url = f"/audio/{user_id}_{character_id}_{datetime.now().timestamp()}.wav"
        
        return VoiceChatResponse(
            character_id=result["character_id"],
            character_name=result["character_name"],
            response=result["response"],
            emotion=result["emotion"],
            audio_url=audio_url,
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音聊天处理失败: {str(e)}")


# === TTS接口 ===
@app.post("/tts")
async def text_to_speech_endpoint(
    text: str,
    voice: str = "Cherry",
    speed: float = 1.0,
    user_id: str = "default"
):
    """文本转语音接口"""
    try:
        audio_data = await audio_service.text_to_speech(
            text=text,
            voice=voice,
            speed=speed
        )
        
        # 这里应该保存文件并返回URL，简化处理
        filename = f"tts_{user_id}_{datetime.now().timestamp()}.wav"
        
        return {
            "success": True,
            "audio_url": f"/audio/{filename}",
            "text": text,
            "voice": voice,
            "duration": len(audio_data) / 24000  # 估算时长
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


# === ASR接口 ===
@app.post("/asr")
async def speech_to_text_endpoint(audio_file: UploadFile = File(...)):
    """语音转文本接口"""
    try:
        audio_data = await audio_file.read()
        
        result = await audio_service.speech_to_text(
            audio_data=audio_data,
            source_format=audio_file.filename.split('.')[-1] if audio_file.filename else 'wav'
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")


# === 对话历史接口 ===
@app.get("/conversations/{user_id}/{character_id}")
async def get_conversation_history(
    user_id: str,
    character_id: str,
    limit: int = 20
):
    """获取对话历史"""
    try:
        history = conversation_graph.get_conversation_history(user_id, character_id)
        
        # 限制返回数量
        if len(history) > limit:
            history = history[-limit:]
        
        return {
            "user_id": user_id,
            "character_id": character_id,
            "conversations": history,
            "total": len(history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")


# === 统计接口 ===
@app.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """获取用户统计信息"""
    try:
        stats = conversation_graph.memory.get_conversation_stats(user_id)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


# === 测试接口 ===
@app.post("/test/audio-pipeline")
async def test_audio_pipeline():
    """测试音频处理管道"""
    try:
        success = await audio_service.test_audio_pipeline()
        return {
            "success": success,
            "message": "音频管道测试完成" if success else "音频管道测试失败"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


# === 启动函数 ===
def start_server():
    """启动AI Agent服务"""
    print(f"🚀 启动FamilyBot AI Agent服务...")
    print(f"📡 服务地址: http://localhost:{Config.AI_AGENT_PORT}")
    print(f"📚 API文档: http://localhost:{Config.AI_AGENT_PORT}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Config.AI_AGENT_PORT,
        reload=False  # 禁用reload避免模块路径问题
    )


if __name__ == "__main__":
    start_server()
