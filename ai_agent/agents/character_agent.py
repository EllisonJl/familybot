"""
角色代理模块 - 实现多个家庭成员角色的AI代理
每个角色有独特的个性、对话风格和记忆系统
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re
import asyncio
from openai import OpenAI
from config import Config, CHARACTER_CONFIGS
from tools.web_search import web_search_tool, should_use_web_search


class CharacterAgent:
    """角色代理基类"""
    
    def __init__(self, character_id: str):
        """
        初始化角色代理
        
        Args:
            character_id: 角色ID (xiyang/meiyang/lanyang)
        """
        if character_id not in CHARACTER_CONFIGS:
            raise ValueError(f"不支持的角色ID: {character_id}")
            
        self.character_id = character_id
        self.config = CHARACTER_CONFIGS[character_id]
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.DASHSCOPE_BASE_URL
        )
        
        # 角色状态
        self.conversation_history: List[Dict[str, Any]] = []
        self.context_memory: Dict[str, Any] = {}
        self.emotional_state = "neutral"  # 情绪状态
        
    def get_system_prompt(self, user_context: Optional[Dict] = None, chat_analysis: Optional[Dict] = None) -> str:
        """
        获取角色的系统提示词
        
        Args:
            user_context: 用户上下文信息
            
        Returns:
            系统提示词
        """
        base_prompt = self.config["system_prompt"]
        
        # 如果有联网搜索结果，添加实时信息
        if user_context and "web_search_result" in user_context:
            search_result = user_context["web_search_result"]
            if search_result and search_result.get("status") == "success" and search_result.get("results"):
                web_info = "\n\n【🔍 最新实时信息】\n"
                web_info += f"基于联网搜索「{search_result.get('query', '')}」的最新结果，请结合以下信息回答：\n\n"
                web_info += search_result.get("summary", "")
                web_info += "\n\n重要提示：请仅使用上述搜索信息的内容来回答用户问题，但不要在回复中包含任何链接、URL或「📎 信息来源」部分。只需要基于这些信息给出自然的回答即可。\n"
                base_prompt += web_info
            elif search_result and search_result.get("status") == "error":
                web_info = "\n\n【搜索提示】\n"
                web_info += f"联网搜索暂时不可用：{search_result.get('summary', '未知错误')}。请基于已有知识回答，并告知用户当前无法获取最新信息。\n"
                base_prompt += web_info
        
        # 如果有RAG搜索结果，添加相关文档信息
        if user_context and "rag_result" in user_context:
            rag_result = user_context["rag_result"]
            if hasattr(rag_result, 'relevant_contexts') and rag_result.relevant_contexts:
                document_info = "\n\n【📚 文档参考信息】\n"
                document_info += "基于用户上传的文档，以下是相关内容，请优先使用这些信息回答用户问题：\n\n"
                
                for i, ctx in enumerate(rag_result.relevant_contexts):
                    source_type = "上传文档" if ctx["source"] == "character_document" else "知识库"
                    document_info += f"{i+1}. 【{source_type}】{ctx['content'][:200]}...\n\n"
                
                document_info += "请根据以上信息准确回答用户问题，不要编造或臆测。如果上述信息中没有相关内容，可以说明没有找到相关信息。\n"
                base_prompt += document_info
        
        # 添加上下文信息
        if user_context:
            context_info = "\n\n当前上下文信息：\n"
            if "time" in user_context:
                context_info += f"- 当前时间：{user_context['time']}\n"
            if "location" in user_context:
                context_info += f"- 用户位置：{user_context['location']}\n"
            if "mood" in user_context:
                context_info += f"- 用户情绪：{user_context['mood']}\n"
            
            base_prompt += context_info
            
        # 添加记忆信息
        if self.context_memory:
            memory_info = "\n\n重要记忆：\n"
            for key, value in self.context_memory.items():
                memory_info += f"- {key}: {value}\n"
            base_prompt += memory_info
        
        # 根据聊天类型添加相应指令
        if chat_analysis:
            if chat_analysis["type"] == "greeting":
                length_instruction = "\n\n回复指导：\n- 给出简短亲切的问候回复（1-2句话）\n- 保持温暖自然的语调"
                base_prompt += length_instruction
                
            elif chat_analysis["type"] == "casual":
                length_instruction = "\n\n回复指导：\n- 给出简洁自然的回复（2-3句话）\n- 适当延续话题，保持轻松愉快"
                base_prompt += length_instruction
                
            elif chat_analysis["type"] == "emotional_support":
                length_instruction = "\n\n回复指导：\n- 给出温暖体贴的回复（3-4句话）\n- 重点关注情感共鸣和心理安慰"
                base_prompt += length_instruction
                
            elif chat_analysis["type"] == "problem_solving":
                # 问题解决场景需要Chain of Thought思维
                cot_instruction = "\n\n深度思考指导（Chain of Thought）：\n"
                cot_instruction += "请在内心进行以下思考过程（但不要在回复中显示思考过程）：\n"
                cot_instruction += "1. **问题分析**: 具体是什么问题？严重程度如何？\n"
                cot_instruction += "2. **原因判断**: 可能的原因有哪些？最主要的是什么？\n"
                cot_instruction += "3. **知识调用**: 需要什么专业知识？有什么相关经验？\n"
                cot_instruction += "4. **方案制定**: 有哪些解决方案？优先级如何？\n"
                cot_instruction += "5. **可行性评估**: 方案是否适合父母的实际情况？\n"
                cot_instruction += "6. **风险考虑**: 有什么需要注意的风险或副作用？\n\n"
                cot_instruction += "然后给出详细实用的建议（4-6句话），包含：\n"
                cot_instruction += "- 具体的解决步骤\n- 注意事项\n- 何时需要寻求专业帮助"
                base_prompt += cot_instruction
        
        return base_prompt
    
    def detect_chat_type(self, user_message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        检测聊天类型，用于决定回复长度和风格
        
        Args:
            user_message: 用户消息
            user_context: 用户上下文（包含RAG结果）
            
        Returns:
            包含聊天类型、长度级别等信息的字典
        """
        message_lower = user_message.lower()
        
        # 实时信息类型（需要联网搜索 - 最长回复）
        if should_use_web_search(user_message):
            return {
                "type": "real_time_info",
                "confidence": 0.95,
                "max_tokens": 400,  # 实时信息需要详细回复
                "length_level": "extra_long",
                "needs_web_search": True
            }
        
        # 文档相关类型（涉及RAG文档 - 长回复）
        if user_context and "rag_result" in user_context:
            rag_result = user_context["rag_result"]
            if hasattr(rag_result, 'relevant_contexts') and rag_result.relevant_contexts:
                return {
                    "type": "document_related",
                    "confidence": 0.9,
                    "max_tokens": 350,  # 文档相关需要详细说明
                    "length_level": "long",
                    "needs_web_search": False
                }
        
        # 问题解决类关键词（需要详细回复）
        problem_keywords = [
            '怎么办', '如何', '什么原因', '为什么', '怎样', '方法', '建议', '帮助',
            '问题', '困难', '麻烦', '不会', '不知道', '解决', '治疗', '病', '疼',
            '头疼', '失眠', '感冒', '咳嗽', '血压', '糖尿病', '心脏'
        ]
        
        # 情感支持类关键词（需要适中回复）
        emotional_keywords = [
            '想你', '想念', '孤独', '寂寞', '难过', '担心', '害怕', '紧张',
            '开心', '高兴', '感动', '回忆', '以前', '小时候'
        ]
        
        # 日常闲聊关键词（简短回复）
        casual_keywords = [
            '你好', '早上好', '晚安', '吃饭', '天气', '今天', '昨天', '明天',
            '看电视', '散步', '睡觉', '起床', '在干什么', '忙吗'
        ]
        
        # 问候语模式（简短回复）
        greeting_patterns = [
            r'^(你好|早上好|中午好|晚上好|晚安)',
            r'(最近.*好吗|身体.*好吗|还好吗)$',
            r'^(在.*吗|忙.*吗)'
        ]
        
        # 检测类型
        chat_type = "casual"
        confidence = 0.5
        max_tokens = 80  # 默认简短回复
        
        # 检查问题解决类
        for keyword in problem_keywords:
            if keyword in user_message:
                chat_type = "problem_solving"
                confidence = 0.9
                max_tokens = 250  # 允许较长回复
                break
        
        # 检查情感支持类
        if chat_type == "casual":
            for keyword in emotional_keywords:
                if keyword in user_message:
                    chat_type = "emotional_support"
                    confidence = 0.8
                    max_tokens = 150  # 中等长度
                    break
        
        # 检查问候语
        if chat_type == "casual":
            for pattern in greeting_patterns:
                if re.search(pattern, user_message):
                    chat_type = "greeting"
                    confidence = 0.9
                    max_tokens = 60  # 很简短
                    break
        
        # 根据消息长度调整
        if len(user_message) < 10:
            max_tokens = min(max_tokens, 80)  # 用户消息很短，回复也要简洁
        elif len(user_message) > 50:
            max_tokens = min(max_tokens + 30, 300)  # 用户消息长，可以适当增加
        
        return {
            "type": chat_type,
            "confidence": confidence,
            "max_tokens": max_tokens,
            "length_level": "short" if max_tokens <= 80 else "medium" if max_tokens <= 150 else "long",
            "needs_web_search": False
        }
    
    def generate_response(
        self, 
        user_message: str, 
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        生成角色回应
        
        Args:
            user_message: 用户消息
            user_context: 用户上下文
            
        Returns:
            包含回应内容、情绪等信息的字典
        """
        try:
            # 检测聊天类型和输出长度
            chat_analysis = self.detect_chat_type(user_message, user_context)
            
            # 确保chat_analysis不为None
            if not chat_analysis:
                print("⚠️ 聊天分析返回空结果，使用默认配置")
                chat_analysis = {
                    "type": "casual",
                    "confidence": 0.5,
                    "max_tokens": 100,
                    "length_level": "medium",
                    "needs_web_search": False
                }
            
            # 如果需要联网搜索，执行搜索
            web_search_result = None
            if chat_analysis and chat_analysis.get("needs_web_search", False):
                print(f"🔍 检测到需要联网搜索: {user_message}")
                try:
                    # 创建事件循环来运行异步搜索
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    web_search_result = loop.run_until_complete(web_search_tool.search(user_message))
                    loop.close()
                    if web_search_result:
                        print(f"✅ 联网搜索完成: {web_search_result.get('total_results', 0)} 个结果")
                    else:
                        print("⚠️ 联网搜索返回空结果")
                except Exception as search_error:
                    print(f"❌ 联网搜索失败: {search_error}")
                    web_search_result = None
            
            # 构建消息历史
            # 将搜索结果添加到用户上下文中
            enhanced_context = user_context.copy() if user_context else {}
            if web_search_result:
                enhanced_context["web_search_result"] = web_search_result
            
            messages = [
                {
                    "role": "system", 
                    "content": self.get_system_prompt(enhanced_context, chat_analysis)
                }
            ]
            
            # 添加历史对话（最近几轮）
            recent_history = self.conversation_history[-Config.MEMORY_WINDOW_SIZE:]
            for item in recent_history:
                messages.append({
                    "role": "user",
                    "content": item["user_message"]
                })
                messages.append({
                    "role": "assistant", 
                    "content": item["assistant_response"]
                })
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 调用LLM生成回应（动态调整max_tokens）
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=chat_analysis.get("max_tokens", 100)
            )
            
            # 安全地提取回应内容
            if not response or not response.choices or not response.choices[0] or not response.choices[0].message:
                raise Exception("LLM返回无效响应")
            
            assistant_response = response.choices[0].message.content
            if not assistant_response:
                raise Exception("LLM返回空内容")
            
            # 更新对话历史
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "assistant_response": assistant_response,
                "user_context": user_context or {},
                "chat_analysis": chat_analysis or {}
            })
            
            # 限制历史长度
            if len(self.conversation_history) > Config.MAX_CONVERSATION_HISTORY:
                self.conversation_history = self.conversation_history[-Config.MAX_CONVERSATION_HISTORY:]
            
            # 情绪分析和上下文更新
            self._update_context_memory(user_message, assistant_response)
            
            return {
                "character_id": self.character_id,
                "character_name": self.config["name"],
                "response": assistant_response,
                "emotion": self.emotional_state,
                "timestamp": datetime.now().isoformat(),
                "voice_config": {
                    "voice": self.config["voice"],
                    "speed": self.config.get("voice_speed", 1.0)
                }
            }
            
        except Exception as e:
            print(f"❌ 生成回应时出错: {e}")
            # 抛出异常让调用方处理，不使用fallback
            raise Exception(f"AI Agent生成回应失败: {str(e)}")
    
    def _update_context_memory(self, user_message: str, assistant_response: str):
        """
        更新上下文记忆
        
        Args:
            user_message: 用户消息
            assistant_response: 助手回应
        """
        # 简单的关键词提取和记忆更新
        keywords = {
            "health": ["身体", "健康", "生病", "医院", "药"],
            "family": ["家人", "孩子", "孙子", "女儿", "儿子"],
            "mood": ["开心", "难过", "生气", "担心", "想念"],
            "activity": ["吃饭", "睡觉", "散步", "看电视", "出门"]
        }
        
        for category, words in keywords.items():
            for word in words:
                if word in user_message:
                    if category not in self.context_memory:
                        self.context_memory[category] = []
                    
                    memory_item = {
                        "content": user_message,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.context_memory[category].append(memory_item)
                    
                    # 保持记忆条目不超过5个
                    if len(self.context_memory[category]) > 5:
                        self.context_memory[category] = self.context_memory[category][-5:]
    
    def get_greeting(self) -> str:
        """获取角色的问候语"""
        return self.config["greeting"]
    
    def get_character_info(self) -> Dict[str, Any]:
        """获取角色信息"""
        return {
            "id": self.character_id,
            "name": self.config["name"],
            "role": self.config["role"],
            "personality": self.config["personality"],
            "voice": self.config["voice"],
            "greeting": self.config["greeting"]
        }
    
    def clear_conversation_history(self):
        """清除对话历史"""
        self.conversation_history = []
        
    def export_conversation_history(self) -> List[Dict[str, Any]]:
        """导出对话历史"""
        return self.conversation_history.copy()


class CharacterManager:
    """角色管理器 - 管理多个角色代理"""
    
    def __init__(self):
        """初始化角色管理器"""
        self.agents: Dict[str, CharacterAgent] = {}
        self.current_character = Config.DEFAULT_CHARACTER
        
        # 初始化所有角色
        for character_id in CHARACTER_CONFIGS.keys():
            self.agents[character_id] = CharacterAgent(character_id)
    
    def switch_character(self, character_id: str) -> bool:
        """
        切换当前角色
        
        Args:
            character_id: 角色ID
            
        Returns:
            是否切换成功
        """
        if character_id in self.agents:
            self.current_character = character_id
            return True
        return False
    
    def get_current_agent(self) -> CharacterAgent:
        """获取当前激活的角色代理"""
        return self.agents[self.current_character]
    
    def get_agent(self, character_id: str) -> Optional[CharacterAgent]:
        """获取指定角色代理"""
        return self.agents.get(character_id)
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """获取所有角色信息"""
        return [agent.get_character_info() for agent in self.agents.values()]
    
    def generate_response(
        self, 
        user_message: str, 
        character_id: Optional[str] = None,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        生成指定角色的回应
        
        Args:
            user_message: 用户消息
            character_id: 角色ID（None则使用当前角色）
            user_context: 用户上下文
            
        Returns:
            角色回应
        """
        if character_id:
            agent = self.get_agent(character_id)
            if not agent:
                raise ValueError(f"角色 {character_id} 不存在")
        else:
            agent = self.get_current_agent()
        
        return agent.generate_response(user_message, user_context)
