"""
角色代理模块 - 实现多个家庭成员角色的AI代理
每个角色有独特的个性、对话风格和记忆系统
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from openai import OpenAI
from config import Config, CHARACTER_CONFIGS


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
        
    def get_system_prompt(self, user_context: Optional[Dict] = None) -> str:
        """
        获取角色的系统提示词
        
        Args:
            user_context: 用户上下文信息
            
        Returns:
            系统提示词
        """
        base_prompt = self.config["system_prompt"]
        
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
            
        return base_prompt
    
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
            # 构建消息历史
            messages = [
                {
                    "role": "system", 
                    "content": self.get_system_prompt(user_context)
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
            
            # 调用LLM生成回应
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_response = response.choices[0].message.content
            
            # 更新对话历史
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "assistant_response": assistant_response,
                "user_context": user_context or {}
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
            return {
                "character_id": self.character_id,
                "character_name": self.config["name"],
                "response": "抱歉，我现在有点累了，一会儿再聊好吗？",
                "emotion": "tired",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
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
