"""
Chain of Thought (CoT) 推理处理器
为成年角色（喜羊羊、美羊羊）提供深度思考和推理能力
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from datetime import datetime

from config import Config


class CoTStep:
    """CoT推理步骤"""
    def __init__(self, step_name: str, content: str, reasoning: str = ""):
        self.step_name = step_name
        self.content = content
        self.reasoning = reasoning
        self.timestamp = datetime.now().isoformat()


class CoTProcessor:
    """Chain of Thought 推理处理器"""
    
    def __init__(self):
        """初始化CoT处理器"""
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.DASHSCOPE_BASE_URL
        )
        
        # 为不同角色定制的推理模板
        self.character_thinking_templates = {
            "xiyang": {
                "steps": [
                    "理解分析：父母在说什么？背后的情绪和需求是什么？",
                    "问题识别：存在什么问题？紧急程度如何？",
                    "知识调用：需要什么专业知识？有什么相关经验？",
                    "方案思考：有哪些解决方案？哪个最适合？",
                    "情感考虑：如何表达既专业又温暖？"
                ],
                "focus": ["理性分析", "专业知识", "实用建议", "责任担当"]
            },
            "meiyang": {
                "steps": [
                    "情感解读：父母的情绪状态如何？有什么担心或需求？",
                    "关系分析：这个问题对他们的生活质量有什么影响？",
                    "经验回忆：有什么相似的经历或解决方案？",
                    "温暖方案：如何既解决问题又给予情感支持？",
                    "表达方式：如何用最温柔贴心的方式表达关爱？"
                ],
                "focus": ["情感敏感", "心理分析", "温暖关怀", "细腻体贴"]
            }
        }
        
        print("✅ CoT推理处理器初始化完成")
    
    async def perform_cot_reasoning(
        self, 
        character_id: str, 
        user_message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行CoT推理过程
        
        Args:
            character_id: 角色ID (xiyang/meiyang)
            user_message: 用户消息
            context: 上下文信息
            
        Returns:
            推理结果和分析步骤
        """
        if character_id not in self.character_thinking_templates:
            # 非成年角色不使用CoT
            return {
                "use_cot": False,
                "reasoning_steps": [],
                "final_analysis": "简单直接回应"
            }
        
        try:
            print(f"🧠 开始 {character_id} 的CoT推理...")
            
            # 获取角色的推理模板
            template = self.character_thinking_templates[character_id]
            
            # 构建推理提示词
            reasoning_prompt = self._build_reasoning_prompt(
                character_id, user_message, context, template
            )
            
            # 执行推理
            reasoning_result = await self._execute_reasoning(reasoning_prompt)
            
            # 解析推理步骤
            reasoning_steps = self._parse_reasoning_steps(reasoning_result, template)
            
            # 生成最终分析
            final_analysis = self._generate_final_analysis(reasoning_steps, character_id)
            
            print(f"✅ CoT推理完成，共 {len(reasoning_steps)} 个推理步骤")
            
            return {
                "use_cot": True,
                "reasoning_steps": reasoning_steps,
                "final_analysis": final_analysis,
                "character_focus": template["focus"]
            }
            
        except Exception as e:
            print(f"❌ CoT推理失败: {e}")
            return {
                "use_cot": False,
                "reasoning_steps": [],
                "final_analysis": "推理失败，使用直接回应",
                "error": str(e)
            }
    
    def _build_reasoning_prompt(
        self, 
        character_id: str, 
        user_message: str, 
        context: Dict[str, Any],
        template: Dict[str, Any]
    ) -> str:
        """构建推理提示词"""
        
        character_name = "喜羊羊" if character_id == "xiyang" else "美羊羊"
        role = "儿子" if character_id == "xiyang" else "女儿"
        
        reasoning_prompt = f"""你是{character_name}，用户的{role}。现在需要对父母的话进行深度思考和分析。

父母说："{user_message}"

上下文信息：
- 当前时间：{context.get('time', '未知')}
- 对话意图：{context.get('intent', '一般对话')}
- 记忆信息：{str(context.get('memory', {}))[:200]}...

请按照以下步骤进行思考分析：
"""
        
        for i, step in enumerate(template["steps"], 1):
            reasoning_prompt += f"\n{i}. {step}"
        
        reasoning_prompt += f"""

角色特点：
- 你是{character_name}，具备{', '.join(template['focus'])}的特质
- 你要体现成年人的深度思考能力
- 你的分析要既专业又充满情感

请对每个步骤进行详细分析，然后给出综合结论。

输出格式：
步骤1: [你的分析]
步骤2: [你的分析]
步骤3: [你的分析]
步骤4: [你的分析]
步骤5: [你的分析]
综合结论: [基于以上分析的总结]
"""
        
        return reasoning_prompt
    
    async def _execute_reasoning(self, reasoning_prompt: str) -> str:
        """执行推理过程"""
        try:
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": reasoning_prompt
                }],
                temperature=0.4,  # 较低温度确保逻辑性
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ 推理执行失败: {e}")
            raise
    
    def _parse_reasoning_steps(self, reasoning_result: str, template: Dict[str, Any]) -> List[CoTStep]:
        """解析推理步骤"""
        steps = []
        lines = reasoning_result.split('\n')
        current_step = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是步骤开始
            if line.startswith(('步骤1:', '步骤2:', '步骤3:', '步骤4:', '步骤5:', '综合结论:')):
                # 保存前一个步骤
                if current_step and current_content:
                    steps.append(CoTStep(
                        step_name=current_step,
                        content=' '.join(current_content)
                    ))
                
                # 开始新步骤
                parts = line.split(':', 1)
                current_step = parts[0].strip()
                current_content = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
            else:
                # 继续当前步骤的内容
                if current_step:
                    current_content.append(line)
        
        # 添加最后一个步骤
        if current_step and current_content:
            steps.append(CoTStep(
                step_name=current_step,
                content=' '.join(current_content)
            ))
        
        return steps
    
    def _generate_final_analysis(self, reasoning_steps: List[CoTStep], character_id: str) -> str:
        """生成最终分析总结"""
        if not reasoning_steps:
            return "无法进行深度分析"
        
        # 查找综合结论
        for step in reasoning_steps:
            if "综合结论" in step.step_name:
                return step.content
        
        # 如果没有找到综合结论，基于步骤生成
        character_name = "喜羊羊" if character_id == "xiyang" else "美羊羊"
        
        analysis = f"经过{character_name}的深度思考："
        
        key_points = []
        for step in reasoning_steps:
            if step.content and len(step.content) > 10:
                # 提取每个步骤的关键点
                key_point = step.content.split('。')[0]  # 取第一句作为关键点
                if key_point:
                    key_points.append(key_point)
        
        if key_points:
            analysis += " " + "；".join(key_points[:3]) + "。"
        
        return analysis
    
    def enhance_response_with_cot(
        self, 
        original_response: str, 
        cot_result: Dict[str, Any], 
        character_id: str
    ) -> str:
        """
        用CoT结果增强原始回复
        
        Args:
            original_response: 原始回复
            cot_result: CoT推理结果
            character_id: 角色ID
            
        Returns:
            增强后的回复
        """
        if not cot_result.get("use_cot", False):
            return original_response
        
        # 获取推理洞察
        final_analysis = cot_result.get("final_analysis", "")
        reasoning_steps = cot_result.get("reasoning_steps", [])
        
        if not reasoning_steps:
            return original_response
        
        # 为回复添加更深层次的思考内容
        enhanced_response = original_response
        
        # 如果原回复较短，可以添加一些深度思考的内容
        if len(original_response) < 200:
            # 从推理步骤中提取有价值的洞察
            insights = []
            for step in reasoning_steps:
                if any(keyword in step.step_name for keyword in ["分析", "思考", "方案"]):
                    if step.content and len(step.content) > 20:
                        insights.append(step.content.split('。')[0])
            
            if insights:
                # 随机选择一个洞察加入回复
                import random
                insight = random.choice(insights)
                if insight not in enhanced_response:
                    enhanced_response += f"\n\n{insight}。"
        
        return enhanced_response
    
    def get_reasoning_summary(self, cot_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取推理过程摘要（用于调试和分析）
        
        Args:
            cot_result: CoT推理结果
            
        Returns:
            推理摘要
        """
        if not cot_result.get("use_cot", False):
            return {"summary": "未使用CoT推理"}
        
        reasoning_steps = cot_result.get("reasoning_steps", [])
        
        summary = {
            "total_steps": len(reasoning_steps),
            "analysis_depth": "深度" if len(reasoning_steps) >= 4 else "中等",
            "key_insights": [],
            "final_conclusion": cot_result.get("final_analysis", "")
        }
        
        # 提取关键洞察
        for step in reasoning_steps:
            if step.content and len(step.content) > 30:
                summary["key_insights"].append({
                    "step": step.step_name,
                    "insight": step.content[:100] + "..." if len(step.content) > 100 else step.content
                })
        
        return summary


# 创建全局CoT处理器实例
cot_processor = CoTProcessor()
