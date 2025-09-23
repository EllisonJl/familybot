"""
对话图工作流 - 使用LangGraph管理对话状态和流程
实现ASR -> 意图分析 -> 路由 -> 角色节点 -> GraphRAG -> 输出 -> TTS的完整流程
"""

from typing import Dict, List, Any, Optional, Literal
from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage, HumanMessage, AIMessage
import json
import random
from datetime import datetime

from ..agents.character_agent import CharacterManager
from ..memory.conversation_memory import ConversationMemory
from ..models.state import ConversationState, Router
from ..graph.router import router
from ..rag.graph_rag import graph_rag
from ..services.audio_service import audio_service


class ConversationGraph:
    """对话图工作流管理器 - 基于新的路由架构"""
    
    def __init__(self):
        """初始化对话图"""
        self.character_manager = CharacterManager()
        self.memory = ConversationMemory()
        self.graph = self._build_graph()
        
        print("✅ 对话图工作流初始化完成")
    
    def _build_graph(self) -> StateGraph:
        """构建新的对话处理图"""
        # 创建状态图
        graph = StateGraph(ConversationState)
        
        # === 添加所有节点 ===
        graph.add_node("start", self._start_node)
        graph.add_node("analyze_and_route_query", self._analyze_and_route_query)
        graph.add_node("route_query", self._route_query_placeholder)  # 路由决策节点
        
        # 角色节点
        graph.add_node("xiyang_node", self._xiyang_character_node)
        graph.add_node("meiyang_node", self._meiyang_character_node)
        graph.add_node("lanyang_node", self._lanyang_character_node)
        graph.add_node("general_response", self._general_response_node)
        
        # 功能节点
        graph.add_node("health_concern_node", self._health_concern_node)
        graph.add_node("emotional_support_node", self._emotional_support_node)
        graph.add_node("knowledge_query_node", self._knowledge_query_node)
        
        # Graph RAG 和输出节点
        graph.add_node("graphrag", self._graphrag_node)
        graph.add_node("model_response_check", self._model_response_check)
        graph.add_node("output", self._output_node)
        
        # === 定义边和条件路由 ===
        graph.set_entry_point("start")
        
        # 基本流程
        graph.add_edge("start", "analyze_and_route_query")
        
        # 条件路由 - 从analyze_and_route_query到不同的角色/功能节点
        graph.add_conditional_edges(
            "analyze_and_route_query",
            lambda state: router.route_query(state),
            {
                "xiyang_node": "xiyang_node",
                "meiyang_node": "meiyang_node", 
                "lanyang_node": "lanyang_node",
                "general_response": "general_response",
                "health_concern_node": "health_concern_node",
                "emotional_support_node": "emotional_support_node",
                "knowledge_query_node": "knowledge_query_node"
            }
        )
        
        # 所有角色/功能节点都连接到graphrag
        for node_name in ["xiyang_node", "meiyang_node", "lanyang_node", "general_response", 
                         "health_concern_node", "emotional_support_node", "knowledge_query_node"]:
            graph.add_edge(node_name, "graphrag")
        
        # graphrag -> model_response_check -> output -> END
        graph.add_edge("graphrag", "model_response_check")
        graph.add_edge("model_response_check", "output")
        graph.add_edge("output", END)
        
        return graph
    
    def _start_node(self, state: ConversationState) -> ConversationState:
        """
        开始节点 - 初始化和预处理
        
        Args:
            state: 对话状态
            
        Returns:
            初始化后的状态
        """
        print(f"🚀 开始处理对话: {state.user_input[:50]}...")
        
        # 清理和标准化输入
        state.user_input = state.user_input.strip()
        
        # 添加到消息历史
        if state.user_input:
            state.messages.append(HumanMessage(content=state.user_input))
            
        # 更新时间戳
        state.timestamp = datetime.now().isoformat()
        
        # 初始化上下文
        if not state.context:
            state.context = {
                "conversation_turn": len(state.messages),
                "session_start": state.timestamp
            }
        
        print(f"📝 用户输入已处理: {state.user_input}")
        return state
    
    async def _analyze_and_route_query(self, state: ConversationState) -> ConversationState:
        """
        分析并路由查询 - 使用Router进行意图识别
        
        Args:
            state: 对话状态
            
        Returns:
            包含路由信息的状态
        """
        print("🔍 开始意图分析和路由...")
        
        # 调用路由器进行分析
        state = await router.analyze_and_route_query(state)
        
        # 从记忆系统获取相关上下文
        memory_context = self.memory.get_relevant_memory(
            user_id=state.user_id,
            character_id=state.selected_character,
            query=state.user_input
        )
        state.memory_context = memory_context
        
        return state
    
    def _route_query_placeholder(self, state: ConversationState) -> ConversationState:
        """
        路由查询占位符节点（实际路由在条件边中处理）
        """
        # 这个节点实际上不会被执行，路由逻辑在条件边中
        return state
    
    def _xiyang_character_node(self, state: ConversationState) -> ConversationState:
        """喜羊羊（儿子）角色节点"""
        return self._generate_character_response(state, "xiyang")
    
    def _meiyang_character_node(self, state: ConversationState) -> ConversationState:
        """美羊羊（女儿）角色节点"""
        return self._generate_character_response(state, "meiyang")
    
    def _lanyang_character_node(self, state: ConversationState) -> ConversationState:
        """懒羊羊（孙子）角色节点"""
        return self._generate_character_response(state, "lanyang")
    
    def _general_response_node(self, state: ConversationState) -> ConversationState:
        """通用回复节点"""
        # 根据上下文选择合适的角色
        preferred_character = state.selected_character or "xiyang"
        return self._generate_character_response(state, preferred_character)
    
    def _health_concern_node(self, state: ConversationState) -> ConversationState:
        """健康关注处理节点"""
        # 健康问题优先使用儿子角色（更理性和专业）
        state.context["response_type"] = "health_focused"
        return self._generate_character_response(state, "xiyang")
    
    def _emotional_support_node(self, state: ConversationState) -> ConversationState:
        """情感支持处理节点"""
        # 情感支持优先使用女儿角色（更温暖贴心）
        state.context["response_type"] = "emotional_support"
        return self._generate_character_response(state, "meiyang")
    
    def _knowledge_query_node(self, state: ConversationState) -> ConversationState:
        """知识查询处理节点"""
        # 知识查询需要更多理性思考，使用儿子角色
        state.context["response_type"] = "knowledge_query"
        state.context["needs_rag"] = True
        return self._generate_character_response(state, "xiyang")
    
    def _generate_character_response(self, state: ConversationState, character_id: str) -> ConversationState:
        """
        生成角色回应的通用方法
        
        Args:
            state: 对话状态
            character_id: 角色ID
            
        Returns:
            更新后的状态
        """
        try:
            # 更新选中的角色
            state.selected_character = character_id
            
            # 构建用户上下文
            user_context = {
                "intent": state.intent,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "memory": state.memory_context,
                "router_info": state.router.model_dump() if state.router else {},
                "response_type": state.context.get("response_type", "normal")
            }
            
            # 生成角色回应
            response_data = self.character_manager.generate_response(
                user_message=state.user_input,
                character_id=character_id,
                user_context=user_context
            )
            
            # 更新状态
            state.assistant_response = response_data["response"]
            state.emotion = response_data["emotion"]
            state.intent = response_data.get("intent", "general")
            state.voice_config = response_data.get("voice_config", {})
            
            # 添加到消息历史
            state.messages.append(AIMessage(content=response_data["response"]))
            
            print(f"🤖 {response_data['character_name']} 生成回应: {response_data['response'][:50]}...")
            
            return state
            
        except Exception as e:
            print(f"❌ 角色回应生成失败: {e}")
            state.assistant_response = "抱歉，我现在有点累了，一会儿再聊好吗？"
            state.emotion = "tired"
            state.error = str(e)
            return state
    
    async def _graphrag_node(self, state: ConversationState) -> ConversationState:
        """
        Graph RAG 知识增强节点
        
        Args:
            state: 对话状态
            
        Returns:
            增强了知识的状态
        """
        print("📚 开始Graph RAG知识增强...")
        
        try:
            # 检查是否需要知识增强
            needs_rag = (
                state.context.get("needs_rag", False) or
                state.router and state.router.type == "knowledge-query" or
                any(keyword in state.user_input.lower() for keyword in 
                    ["怎么", "为什么", "什么是", "如何", "健康", "养生", "疾病"])
            )
            
            if needs_rag:
                # 根据路由类型确定知识域
                domain = None
                if state.router:
                    if "health" in state.router.type or "健康" in state.user_input:
                        domain = "health"
                    elif "emotion" in state.router.type or any(word in state.user_input for word in ["孤单", "难过", "开心"]):
                        domain = "emotion"
                    elif "family" in state.router.type:
                        domain = "family"
                
                # 执行知识检索
                rag_result = await graph_rag.query_knowledge(
                    query=state.user_input,
                    domain=domain,
                    limit=3
                )
                
                state.rag_context = rag_result.relevant_contexts
                
                print(f"✅ Graph RAG增强完成，获得 {len(state.rag_context)} 个知识上下文")
            else:
                print("ℹ️ 当前对话不需要知识增强")
                state.rag_context = []
            
            return state
            
        except Exception as e:
            print(f"❌ Graph RAG处理失败: {e}")
            state.rag_context = []
            return state
    
    def _model_response_check(self, state: ConversationState) -> ConversationState:
        """
        模型回复检测节点 - 检查和优化模型回复
        
        Args:
            state: 对话状态
            
        Returns:
            检测后的状态
        """
        print("🔍 检查模型回复质量...")
        
        try:
            response = state.assistant_response
            
            # 基本质量检查
            quality_checks = {
                "length_ok": 10 <= len(response) <= 500,
                "not_empty": bool(response.strip()),
                "no_error_keywords": not any(word in response for word in ["错误", "失败", "抱歉"]),
                "appropriate_tone": True  # 简化处理
            }
            
            # 如果有RAG上下文，检查是否有效利用
            if state.rag_context:
                state.context["rag_enhanced"] = True
                print(f"📚 回复已使用 {len(state.rag_context)} 个知识上下文增强")
            
            # 记录质量分数
            quality_score = sum(quality_checks.values()) / len(quality_checks)
            state.context["response_quality"] = quality_score
            
            # 如果质量太低，使用备用回复
            if quality_score < 0.5:
                print("⚠️ 回复质量较低，使用备用回复")
                from ..config import CHARACTER_CONFIGS
                character_config = CHARACTER_CONFIGS.get(state.selected_character, {})
                
                backup_responses = [
                    f"我是{character_config.get('name', '家人')}，很高兴和你聊天！",
                    "谢谢你和我分享这些，我会一直陪伴着你的。",
                    "你说得很有道理，我们继续聊聊吧！"
                ]
                state.assistant_response = random.choice(backup_responses)
            
            print(f"✅ 回复质量检查完成 (质量分数: {quality_score:.2f})")
            return state
            
        except Exception as e:
            print(f"❌ 模型回复检查失败: {e}")
            return state
    
    def _output_node(self, state: ConversationState) -> ConversationState:
        """
        输出节点 - 准备最终输出并存储记忆
        
        Args:
            state: 对话状态
            
        Returns:
            最终状态
        """
        print("📤 准备最终输出...")
        
        try:
            # 存储对话到记忆系统
            conversation_data = {
                "user_message": state.user_input,
                "assistant_response": state.assistant_response,
                "intent": state.intent,
                "emotion": state.emotion,
                "timestamp": state.timestamp,
                "context": state.context
            }
            
            self.memory.store_conversation(
                user_id=state.user_id,
                character_id=state.selected_character,
                conversation=conversation_data
            )
            
            # 标记输出就绪
            state.output_ready = True
            
            print(f"✅ 对话输出完成，已存储到记忆系统")
            return state
            
        except Exception as e:
            print(f"❌ 输出处理失败: {e}")
            state.error = str(e)
            return state
    
    async def process_conversation(
        self, 
        user_input: str,
        user_id: str = "default",
        character_id: str = "xiyang",
        audio_input: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        处理完整的对话流程 - 异步版本
        
        Args:
            user_input: 用户输入文本
            user_id: 用户ID
            character_id: 角色ID (初始偏好，可能被路由器覆盖)
            audio_input: 音频输入（可选）
            
        Returns:
            处理结果
        """
        try:
            # 创建初始状态
            initial_state = ConversationState(
                user_id=user_id,
                user_input=user_input,
                selected_character=character_id,
                timestamp=datetime.now().isoformat(),
                messages=[],
                context={},
                memory_context={},
                rag_context=[],
                voice_config={}
            )
            
            if audio_input:
                initial_state.audio_input = audio_input
            
            print(f"🚀 开始新的对话流程: {user_input[:30]}...")
            
            # 编译并运行图
            app = self.graph.compile()
            final_state = await app.ainvoke(initial_state)
            
            # 确保final_state是ConversationState对象
            if not hasattr(final_state, 'selected_character'):
                print(f"⚠️ final_state类型异常: {type(final_state)}")
                # 如果是字典，转换为对象属性访问
                if isinstance(final_state, dict):
                    final_state = type('obj', (object,), final_state)
                else:
                    raise Exception(f"Unexpected final_state type: {type(final_state)}")
            
            # 构建返回结果
            from ..config import CHARACTER_CONFIGS
            character_config = CHARACTER_CONFIGS.get(final_state.selected_character, {})
            
            result = {
                "character_id": final_state.selected_character,
                "character_name": character_config.get("name", "AI助手"),
                "response": final_state.assistant_response,
                "emotion": final_state.emotion or "neutral",
                "intent": final_state.intent or "general",
                "voice_config": final_state.voice_config,
                "timestamp": final_state.timestamp,
                "context": final_state.context,
                "router_info": final_state.router.model_dump() if final_state.router else None,
                "rag_enhanced": len(final_state.rag_context) > 0
            }
            
            print(f"✅ 对话流程完成: {final_state.assistant_response[:50]}...")
            return result
            
        except Exception as e:
            print(f"❌ 对话处理出错: {e}")
            return {
                "character_id": character_id,
                "character_name": "系统",
                "response": "抱歉，我现在有点问题，请稍后再试。",
                "emotion": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def switch_character(self, character_id: str) -> bool:
        """切换角色"""
        return self.character_manager.switch_character(character_id)
    
    def get_available_characters(self) -> List[Dict[str, Any]]:
        """获取可用角色列表"""
        return self.character_manager.get_all_characters()
    
    def get_conversation_history(self, user_id: str, character_id: str) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.memory.get_conversation_history(user_id, character_id)
