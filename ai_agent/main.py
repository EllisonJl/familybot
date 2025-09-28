"""
FamilyBot AI Agent 主服务
提供FastAPI接口，集成所有AI功能模块
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from typing import Optional, Dict, Any, List
import asyncio
import os
from datetime import datetime

from config import Config
from graph.conversation_graph import ConversationGraph
from services.audio_service import audio_service
from rag.graph_rag import graph_rag
from tools.web_search import web_search_tool, perform_web_search


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
    voice_config: Optional[Dict[str, Any]] = None
    force_web_search: Optional[bool] = False  # 强制启用联网搜索


class ChatResponse(BaseModel):
    """聊天响应模型"""
    character_id: str
    character_name: str
    response: str
    emotion: str
    timestamp: str
    voice_config: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None  # 添加音频URL字段
    audio_base64: Optional[str] = None  # 添加音频Base64字段
    web_search_used: Optional[bool] = False  # 是否使用了联网搜索
    web_search_query: Optional[str] = None  # 搜索查询词
    web_search_results_count: Optional[int] = 0  # 搜索结果数量
    # 图片生成相关字段
    image_url: Optional[str] = None  # 生成的图片URL
    image_base64: Optional[str] = None  # 生成的图片Base64编码
    image_description: Optional[str] = None  # 用户提供的图片描述
    enhanced_prompt: Optional[str] = None  # AI增强后的提示词


class WebSearchResponse(BaseModel):
    """联网搜索响应模型"""
    query: str
    timestamp: str
    total_results: int
    results: List[Dict[str, Any]]
    summary: str
    status: str


class VoiceChatRequest(BaseModel):
    """语音聊天请求模型"""
    user_id: str = "default"
    character_id: str = "xiyang"
    context: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    success: bool = Field(description="上传是否成功")
    message: str = Field(description="响应消息")
    file_id: Optional[str] = Field(default=None, description="文件ID")
    filename: Optional[str] = Field(default=None, description="文件名")


class DocumentListResponse(BaseModel):
    """文档列表响应模型"""
    files: List[Dict[str, Any]] = Field(description="文档列表")
    total: int = Field(description="文档总数")


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
    """获取角色问候语，包含TTS音频"""
    try:
        agent = conversation_graph.character_manager.get_agent(character_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"角色 {character_id} 不存在")
        
        greeting = agent.get_greeting()
        
        # 生成问候语的TTS音频
        try:
            from services.audio_service import AudioService
            audio_service = AudioService()
            
            # 获取角色的音色配置
            voice_config = agent.config.get("voice_config", {})
            voice_speed = voice_config.get("speed", agent.config.get("voice_speed", 1.0))
            
            print(f"🎵 为角色 {character_id} 生成问候语TTS...")
            tts_audio = await audio_service.generate_character_voice(
                character_id=character_id,
                text=greeting,
                speed=voice_speed
            )
            
            if tts_audio:
                import base64
                from datetime import datetime
                audio_base64 = base64.b64encode(tts_audio).decode('utf-8')
                audio_url = f"/audio/greeting_{character_id}_{datetime.now().timestamp()}.wav"
                print(f"✅ 问候语TTS生成成功: {len(tts_audio)} 字节")
                
                return {
                    "character_id": character_id,
                    "character_name": agent.config["name"],
                    "greeting": greeting,
                    "audio_base64": audio_base64,
                    "audio_url": audio_url
                }
            else:
                print("⚠️ 问候语TTS生成失败，返回纯文本")
                
        except Exception as tts_error:
            print(f"❌ 问候语TTS生成出错: {tts_error}")
            # TTS失败不影响问候语返回
        
        # 如果TTS失败，只返回文本
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
        print(f"🎵 接收到音色配置: {request.voice_config}")  # 添加调试日志
        
        # 使用简化的记忆系统 - 直接调用角色管理器但添加记忆功能
        from agents.character_agent import CharacterManager
        from datetime import datetime
        
        character_manager = CharacterManager()
        agent = character_manager.get_agent(request.character_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"角色 {request.character_id} 不存在")
        
        print(f"🧠 启用记忆系统 - 用户ID: {request.user_id}, 角色: {request.character_id}")
        
        # 从记忆系统获取历史对话
        conversation_history = conversation_graph.get_conversation_history(request.user_id, request.character_id)
        print(f"📚 加载历史对话: {len(conversation_history)} 条记录")
        
        # 如果有历史记录，更新agent的对话历史
        if conversation_history:
            agent.conversation_history = []
            for conv in conversation_history[-10:]:  # 最近10条
                # 检查conv是否为None
                if conv:
                    agent.conversation_history.append({
                        "timestamp": conv.get("timestamp", ""),
                        "user_message": conv.get("user_message", ""),
                        "assistant_response": conv.get("assistant_response", ""),
                        "user_context": conv.get("context", {}),
                        "chat_analysis": {}
                    })
                else:
                    print("⚠️ 发现空的历史对话记录，跳过")
        
        # 检查是否需要联网搜索
        web_search_result = None
        web_search_used = False
        if request.force_web_search or web_search_tool.should_search(request.message):
            print(f"🔍 启动联网搜索: {request.message}")
            try:
                web_search_result = await perform_web_search(request.message)
                web_search_used = True
                print(f"✅ 联网搜索完成: {web_search_result.get('total_results', 0)} 个结果")
            except Exception as search_error:
                print(f"❌ 联网搜索失败: {search_error}")
                web_search_result = None

        # 使用GraphRAG搜索相关知识（包括角色文档）
        print(f"🔍 使用GraphRAG搜索相关知识...")
        rag_result = await graph_rag.query_knowledge(
            query=request.message,
            character_id=request.character_id
        )
        
        # 确保rag_result不为None
        if not rag_result:
            print("⚠️ GraphRAG搜索返回空结果")
            rag_result = type('RAGResult', (), {'relevant_contexts': []})()
        
        print(f"📚 GraphRAG搜索结果: {len(rag_result.relevant_contexts) if rag_result.relevant_contexts else 0} 个相关上下文")
        if rag_result.relevant_contexts:
            for ctx in rag_result.relevant_contexts:
                print(f"   - {ctx['source']}: {ctx['content'][:50]}...")
        
        # 检查是否需要生成图片
        image_result = None
        image_description = None
        from services.image_service import image_service
        
        if image_service.should_generate_image(request.message):
            print(f"🎨 检测到图片生成请求，开始生成图片...")
            image_description = image_service.extract_image_description(request.message)
            print(f"🖼️ 图片描述: {image_description}")
            
            # 生成图片
            image_result = await image_service.generate_image(
                user_prompt=image_description,
                character_id=request.character_id,
                style_preference=None
            )
            
            print(f"🎨 图片生成结果: {'成功' if image_result.get('success') else '失败'}")
        
        # 构建用户上下文
        user_context = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "user_id": request.user_id,
            "thread_id": request.thread_id or f"{request.user_id}_{request.character_id}",
            "rag_result": rag_result,  # 添加GraphRAG搜索结果
            "web_search_result": web_search_result,  # 添加联网搜索结果
            "image_result": image_result,  # 添加图片生成结果
            "image_description": image_description  # 添加图片描述
        }
        
        # 生成回复
        response_data = agent.generate_response(request.message, user_context)
        
        # 如果生成了图片，获取角色对图片的回应并添加到响应中
        if image_result:
            character_image_response = await image_service.get_character_image_response(
                request.character_id, image_result
            )
            # 将角色的图片回应添加到原回复中
            if image_result.get("success"):
                response_data["response"] = character_image_response
                response_data["image_url"] = image_result.get("image_url")
                response_data["image_base64"] = image_result.get("image_base64") 
                response_data["image_description"] = image_description
                response_data["enhanced_prompt"] = image_result.get("enhanced_prompt")
            else:
                response_data["response"] = character_image_response
        
        # 保存对话到记忆系统
        conversation_data = {
            "user_message": request.message,
            "assistant_response": response_data.get("response", ""),
            "character_id": request.character_id,
            "intent": response_data.get("intent", "general"),
            "emotion": response_data.get("emotion", "neutral"),
            "timestamp": datetime.now().isoformat(),
            "context": request.context or {}
        }
        
        conversation_graph.memory.store_conversation(
            user_id=request.user_id,
            character_id=request.character_id,
            conversation=conversation_data
        )
        print(f"💾 对话已保存到记忆系统")
        
        # 如果前端传递了voice_config，优先使用前端的配置
        if request.voice_config:
            print(f"🎵 使用前端传递的音色配置: {request.voice_config}")
            response_data["voice_config"] = request.voice_config
        else:
            print(f"🎵 使用默认角色音色配置: {response_data.get('voice_config')}")
        
        print(f"✅ 生成回复: {response_data['character_name']} -> {response_data['response'][:50]}...")
        
        # 生成语音音频
        final_voice_config = response_data.get("voice_config", {})
        character_voice = final_voice_config.get("voice", "Cherry")
        voice_speed = final_voice_config.get("speed", 1.0)
        
        print(f"🎵 开始生成语音: voice={character_voice}, speed={voice_speed}")
        
        try:
            # 调用TTS服务
            from services.audio_service import AudioService
            audio_service = AudioService()
            
            tts_audio = await audio_service.generate_character_voice(
                character_id=request.character_id,
                text=response_data["response"],
                speed=voice_speed
            )
            
            if tts_audio:
                # 保存音频文件（简化处理）
                import base64
                audio_base64 = base64.b64encode(tts_audio).decode('utf-8')
                audio_url = f"/audio/{request.user_id}_{request.character_id}_{datetime.now().timestamp()}.wav"
                print(f"✅ TTS生成成功: {len(tts_audio)} 字节, URL: {audio_url}")
            else:
                audio_base64 = None
                audio_url = None
                print("⚠️ TTS生成失败")
                
        except Exception as e:
            print(f"❌ TTS处理失败: {e}")
            audio_base64 = None
            audio_url = None
        
        return ChatResponse(
            character_id=response_data["character_id"],
            character_name=response_data["character_name"],
            response=response_data["response"],
            emotion=response_data["emotion"],
            timestamp=response_data["timestamp"],
            voice_config=response_data.get("voice_config"),
            audio_url=audio_url,  # 添加音频URL
            audio_base64=audio_base64,  # 添加音频Base64
            web_search_used=web_search_used,  # 是否使用了联网搜索
            web_search_query=request.message if web_search_used else None,  # 搜索查询词
            web_search_results_count=web_search_result.get('total_results', 0) if web_search_result else 0,  # 搜索结果数量
            # 图片生成相关字段
            image_url=response_data.get("image_url"),
            image_base64=response_data.get("image_base64"),
            image_description=response_data.get("image_description"),
            enhanced_prompt=response_data.get("enhanced_prompt")
        )
        
    except Exception as e:
        print(f"❌ 聊天处理失败: {str(e)}")
        # 返回明确的错误信息，不使用模糊的fallback
        try:
            from config import CHARACTER_CONFIGS
        except ImportError:
            CHARACTER_CONFIGS = {}
        
        character_config = CHARACTER_CONFIGS.get(request.character_id, {})
        error_message = f"处理失败: {str(e)[:100]}..."
        return ChatResponse(
            character_id=request.character_id,
            character_name=character_config.get("name", "系统"),
            response=error_message,
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
        
        # 语音合成 - 使用角色专属TTS函数
        voice_config = result.get("voice_config", {})
        voice_speed = voice_config.get("speed", 1.0)
        
        print(f"🎵 使用角色专用TTS函数 为角色 {character_id}")
        
        tts_audio = await audio_service.generate_character_voice(
            character_id=character_id,
            text=result["response"],
            speed=voice_speed
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


# === 文件上传接口 ===
@app.post("/upload-document", response_model=FileUploadResponse)
async def upload_document(
    character_id: str = Form(..., description="角色ID"),
    user_id: str = Form(..., description="用户ID"),
    file: UploadFile = File(..., description="上传的文件")
):
    """
    上传文档到角色知识库
    """
    try:
        print(f"📤 接收文档上传请求: {file.filename} -> 角色: {character_id}")
        
        # 检查文件大小（限制为10MB）
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="文件大小不能超过10MB")
        
        # 读取文件内容
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(status_code=400, detail="文件内容为空")
        
        # 调用GraphRAG系统处理文档
        success, message = await graph_rag.add_document_knowledge(
            character_id=character_id,
            file_content=file_content,
            filename=file.filename,
            user_id=user_id
        )
        
        if success:
            print(f"✅ 文档上传成功: {file.filename}")
            return FileUploadResponse(
                success=True,
                message=message,
                filename=file.filename
            )
        else:
            print(f"❌ 文档上传失败: {message}")
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 文档上传处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")


@app.get("/documents/{character_id}", response_model=DocumentListResponse)
async def get_character_documents(character_id: str):
    """
    获取角色的所有文档
    """
    try:
        print(f"📄 获取角色文档: {character_id}")
        
        documents = graph_rag.get_character_documents(character_id)
        
        return DocumentListResponse(
            files=documents,
            total=len(documents)
        )
        
    except Exception as e:
        print(f"❌ 获取角色文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@app.delete("/documents/{character_id}/{file_id}")
async def delete_character_document(character_id: str, file_id: str):
    """
    删除角色文档
    """
    try:
        print(f"🗑️ 删除角色文档: {character_id}/{file_id}")
        
        success = graph_rag.delete_character_document(character_id, file_id)
        
        if success:
            return {
                "success": True, 
                "message": "文档删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail="文档不存在或删除失败")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 删除角色文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


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


# === 联网搜索接口 ===
@app.post("/web-search", response_model=WebSearchResponse)
async def perform_web_search_api(query: str = Form(..., description="搜索查询")):
    """
    执行联网搜索
    
    Args:
        query: 搜索查询词
    
    Returns:
        搜索结果
    """
    try:
        print(f"🔍 收到联网搜索请求: {query}")
        
        # 执行搜索
        search_result = await perform_web_search(query)
        
        if search_result:
            print(f"✅ 联网搜索完成: {search_result.get('total_results', 0)} 个结果")
            return WebSearchResponse(**search_result)
        else:
            return WebSearchResponse(
                query=query,
                timestamp=datetime.now().isoformat(),
                total_results=0,
                results=[],
                summary="搜索失败，请稍后重试",
                status="error"
            )
    
    except Exception as e:
        print(f"❌ 联网搜索失败: {e}")
        return WebSearchResponse(
            query=query,
            timestamp=datetime.now().isoformat(),
            total_results=0,
            results=[],
            summary=f"搜索出错: {str(e)}",
            status="error"
        )


@app.get("/web-search/test")
async def test_web_search():
    """测试联网搜索功能"""
    try:
        test_query = "Hello world"
        result = await perform_web_search(test_query)
        return {
            "success": True,
            "test_query": test_query,
            "results_count": result.get('total_results', 0) if result else 0,
            "message": "联网搜索功能正常" if result else "联网搜索功能异常"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"联网搜索测试失败: {str(e)}"
        }


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
