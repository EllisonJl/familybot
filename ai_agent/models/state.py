"""
状态模型定义
定义LangGraph中使用的状态数据结构
"""

from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field
from langchain.schema import BaseMessage


class Router(BaseModel):
    """路由器模型 - 用于意图识别和路由决策"""
    
    type: Literal[
        "character-xiyang",     # 喜羊羊（儿子）对话
        "character-meiyang",    # 美羊羊（女儿）对话  
        "character-lanyang",    # 懒羊羊（孙子）对话
        "general-query",        # 一般查询
        "health-concern",       # 健康关注
        "emotional-support",    # 情感支持
        "knowledge-query"       # 知识查询（需要RAG）
    ] = Field(description="查询类型，决定路由到哪个处理节点")
    
    logic: str = Field(description="路由决策的逻辑说明")
    
    confidence: float = Field(
        default=0.0, 
        ge=0.0, 
        le=1.0, 
        description="路由决策的置信度"
    )
    
    character_preference: Optional[str] = Field(
        default=None,
        description="推荐的角色ID（如果检测到特定需求）"
    )


class ConversationState(BaseModel):
    """对话状态 - LangGraph中的主要状态对象"""
    
    # 基本信息
    user_id: str = Field(description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID") 
    timestamp: str = Field(description="时间戳")
    
    # 消息相关
    messages: List[BaseMessage] = Field(default_factory=list, description="对话消息历史")
    user_input: str = Field(default="", description="用户当前输入")
    assistant_response: str = Field(default="", description="AI助手回复")
    
    # 路由相关
    router: Optional[Router] = Field(default=None, description="路由信息")
    selected_character: str = Field(default="xiyang", description="选中的角色ID")
    role: str = Field(default="elderly", description="用户角色（elderly/adult/child）")
    
    # 意图和情绪
    intent: str = Field(default="general", description="用户意图")
    emotion: str = Field(default="neutral", description="情绪状态")
    urgency: str = Field(default="normal", description="紧急程度：low/normal/high")
    
    # 上下文信息
    context: Dict[str, Any] = Field(default_factory=dict, description="对话上下文")
    memory_context: Dict[str, Any] = Field(default_factory=dict, description="记忆上下文")
    rag_context: List[Dict[str, Any]] = Field(default_factory=list, description="RAG检索的上下文")
    
    # 音频相关（可选）
    audio_input: Optional[bytes] = Field(default=None, description="音频输入数据")
    audio_output: Optional[bytes] = Field(default=None, description="音频输出数据")
    
    # 输出相关
    voice_config: Dict[str, Any] = Field(default_factory=dict, description="语音配置")
    output_ready: bool = Field(default=False, description="输出是否准备就绪")
    
    # 错误处理
    error: Optional[str] = Field(default=None, description="错误信息")
    retry_count: int = Field(default=0, description="重试次数")
    
    class Config:
        arbitrary_types_allowed = True


class IntentAnalysisResult(BaseModel):
    """意图分析结果"""
    
    primary_intent: str = Field(description="主要意图")
    secondary_intents: List[str] = Field(default_factory=list, description="次要意图")
    emotion_detected: str = Field(default="neutral", description="检测到的情绪")
    urgency_level: str = Field(default="normal", description="紧急程度")
    character_suggestion: Optional[str] = Field(default=None, description="建议的角色")
    confidence_score: float = Field(default=0.0, description="置信度分数")
    reasoning: str = Field(description="分析推理过程")


class GraphRAGResult(BaseModel):
    """Graph RAG检索结果"""
    
    relevant_contexts: List[Dict[str, Any]] = Field(default_factory=list, description="相关上下文")
    knowledge_sources: List[str] = Field(default_factory=list, description="知识来源")
    confidence: float = Field(default=0.0, description="检索置信度")
    query_expansion: List[str] = Field(default_factory=list, description="查询扩展")


class CharacterResponse(BaseModel):
    """角色回复结果"""
    
    character_id: str = Field(description="角色ID")
    character_name: str = Field(description="角色名称")
    response_text: str = Field(description="回复文本")
    emotion: str = Field(default="neutral", description="回复情绪")
    voice_config: Dict[str, Any] = Field(default_factory=dict, description="语音配置")
    generated_at: str = Field(description="生成时间")
    
    # 回复质量指标
    relevance_score: float = Field(default=0.0, description="相关性分数")
    empathy_score: float = Field(default=0.0, description="共情分数")
    safety_score: float = Field(default=0.0, description="安全性分数")
