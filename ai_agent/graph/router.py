"""
路由系统实现
实现analyze_and_route_query和route_query功能
"""

import json
from typing import Literal, cast
from openai import OpenAI
from langchain.schema import HumanMessage

from ..config import Config
from ..models.state import ConversationState, Router, IntentAnalysisResult
from ..prompts.router_prompts import ROUTER_SYSTEM_PROMPT, INTENT_ANALYSIS_PROMPT


class FamilyBotRouter:
    """FamilyBot路由器 - 负责意图识别和路由决策"""
    
    def __init__(self):
        """初始化路由器"""
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.DASHSCOPE_BASE_URL
        )
        print("✅ FamilyBot路由器初始化完成")
    
    async def analyze_and_route_query(self, state: ConversationState) -> ConversationState:
        """
        分析用户查询并确定路由方向
        
        Args:
            state: 当前对话状态
            
        Returns:
            更新后的对话状态（包含路由信息）
        """
        try:
            print(f"🔍 开始分析用户查询: {state.user_input[:50]}...")
            
            # 构建分析消息
            messages = [
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT}
            ]
            
            # 添加历史上下文（最近3轮对话）
            recent_messages = state.messages[-6:] if len(state.messages) > 6 else state.messages
            for msg in recent_messages:
                if hasattr(msg, 'content'):
                    role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
                    messages.append({"role": role, "content": msg.content})
            
            # 添加当前用户输入
            messages.append({"role": "user", "content": state.user_input})
            
            # 调用LLM进行路由分析
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=0.3,  # 较低温度确保路由一致性
                max_tokens=200,
                response_format={"type": "json_object"}  # 强制JSON输出
            )
            
            # 解析路由结果
            route_text = response.choices[0].message.content
            route_data = json.loads(route_text)
            
            # 创建Router对象
            router = Router(
                type=route_data.get("type", "general-query"),
                logic=route_data.get("logic", "默认路由"),
                confidence=route_data.get("confidence", 0.5),
                character_preference=route_data.get("character_preference")
            )
            
            # 更新状态
            state.router = router
            
            # 根据路由结果设置推荐角色
            if router.character_preference:
                state.selected_character = router.character_preference
            
            print(f"✅ 路由分析完成: {router.type} (置信度: {router.confidence:.2f})")
            print(f"📝 路由逻辑: {router.logic}")
            
            return state
            
        except Exception as e:
            print(f"❌ 路由分析失败: {e}")
            # 设置默认路由
            state.router = Router(
                type="general-query",
                logic=f"分析失败，使用默认路由: {str(e)}",
                confidence=0.1
            )
            return state
    
    def route_query(self, state: ConversationState) -> Literal[
        "xiyang_node", 
        "meiyang_node", 
        "lanyang_node", 
        "general_response",
        "health_concern_node",
        "emotional_support_node", 
        "knowledge_query_node"
    ]:
        """
        根据分析结果决定路由到哪个节点
        
        Args:
            state: 包含路由信息的对话状态
            
        Returns:
            下一个处理节点的名称
        """
        if not state.router:
            print("⚠️ 没有路由信息，使用默认路由")
            return "general_response"
        
        route_type = state.router.type
        confidence = state.router.confidence
        
        print(f"🎯 执行路由决策: {route_type} (置信度: {confidence:.2f})")
        
        # 低置信度时的安全处理
        if confidence < 0.3:
            print("⚠️ 路由置信度较低，使用一般回复")
            return "general_response"
        
        # 角色路由
        if route_type == "character-xiyang":
            print("👨 路由到儿子角色 (喜羊羊)")
            return "xiyang_node"
        elif route_type == "character-meiyang":
            print("👩 路由到女儿角色 (美羊羊)")
            return "meiyang_node"
        elif route_type == "character-lanyang":
            print("👶 路由到孙子角色 (懒羊羊)")
            return "lanyang_node"
        
        # 功能路由
        elif route_type == "health-concern":
            print("🏥 路由到健康关注处理")
            return "health_concern_node"
        elif route_type == "emotional-support":
            print("💝 路由到情感支持处理")
            return "emotional_support_node"
        elif route_type == "knowledge-query":
            print("📚 路由到知识查询处理")
            return "knowledge_query_node"
        
        # 默认路由
        else:
            print("📝 路由到一般回复处理")
            return "general_response"
    
    async def analyze_intent_detailed(self, state: ConversationState) -> IntentAnalysisResult:
        """
        详细的意图分析（用于复杂场景）
        
        Args:
            state: 对话状态
            
        Returns:
            详细的意图分析结果
        """
        try:
            # 构建分析消息
            messages = [
                {"role": "system", "content": INTENT_ANALYSIS_PROMPT},
                {"role": "user", "content": f"请分析这段话的意图：{state.user_input}"}
            ]
            
            # 调用LLM进行详细分析
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=300
            )
            
            analysis_text = response.choices[0].message.content
            
            # 这里可以进一步解析分析结果
            # 简化处理，返回基本结果
            return IntentAnalysisResult(
                primary_intent="companionship",
                emotion_detected="neutral",
                character_suggestion=state.selected_character,
                confidence_score=0.8,
                reasoning=analysis_text[:200]
            )
            
        except Exception as e:
            print(f"❌ 详细意图分析失败: {e}")
            return IntentAnalysisResult(
                primary_intent="unknown",
                emotion_detected="neutral",
                confidence_score=0.1,
                reasoning=f"分析失败: {str(e)}"
            )


# 创建全局路由器实例
router = FamilyBotRouter()
