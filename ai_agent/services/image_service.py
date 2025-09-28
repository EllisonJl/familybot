"""
图片生成服务模块
支持根据用户描述生成个性化图片
"""

import os
import base64
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional
from openai import OpenAI
from config import Config


class ImageService:
    """图片生成服务类"""
    
    def __init__(self):
        """初始化图片生成服务"""
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.default_size = "1024x1024"
        self.default_quality = "standard"
        
    async def generate_image(
        self, 
        user_prompt: str, 
        character_id: str,
        style_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        根据用户描述和角色特点生成图片
        
        Args:
            user_prompt: 用户的图片描述
            character_id: 角色ID
            style_preference: 风格偏好（可选）
            
        Returns:
            包含图片信息的字典
        """
        try:
            print(f"🎨 开始生成图片 - 角色: {character_id}, 描述: {user_prompt[:50]}...")
            
            # 1. 根据角色特点优化提示词
            enhanced_prompt = self._enhance_prompt_by_character(
                user_prompt, character_id, style_preference
            )
            
            print(f"🎯 优化后的提示词: {enhanced_prompt[:100]}...")
            
            # 2. 调用OpenAI DALL-E生成图片
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=self.default_size,
                quality=self.default_quality,
                n=1,
                response_format="url"
            )
            
            # 3. 处理响应
            image_url = response.data[0].url
            revised_prompt = getattr(response.data[0], 'revised_prompt', enhanced_prompt)
            
            print(f"✅ 图片生成成功: {image_url}")
            
            # 4. 下载图片并转换为base64（可选）
            image_base64 = await self._download_and_encode_image(image_url)
            
            return {
                "success": True,
                "image_url": image_url,
                "image_base64": image_base64,
                "original_prompt": user_prompt,
                "enhanced_prompt": enhanced_prompt,
                "revised_prompt": revised_prompt,
                "character_id": character_id,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "size": self.default_size,
                    "quality": self.default_quality,
                    "model": "dall-e-3"
                }
            }
            
        except Exception as e:
            print(f"❌ 图片生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "character_id": character_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def _enhance_prompt_by_character(
        self, 
        user_prompt: str, 
        character_id: str,
        style_preference: Optional[str] = None
    ) -> str:
        """
        根据角色特点增强图片生成提示词
        
        Args:
            user_prompt: 用户原始描述
            character_id: 角色ID
            style_preference: 风格偏好
            
        Returns:
            增强后的提示词
        """
        # 角色特点映射
        character_styles = {
            "xiyang": {
                "style": "成熟稳重风格，商务风，现代简约",
                "color_tone": "蓝色系、灰色系，专业色调",
                "mood": "理性、专业、可靠的氛围"
            },
            "meiyang": {
                "style": "温馨甜美风格，日系风，清新自然", 
                "color_tone": "粉色系、暖色调，柔和色彩",
                "mood": "温暖、治愈、浪漫的氛围"
            },
            "lanyang": {
                "style": "童趣可爱风格，卡通风，活泼明快",
                "color_tone": "彩虹色系、明亮色调，对比鲜明",
                "mood": "欢快、活泼、童真的氛围"
            }
        }
        
        # 获取角色风格
        char_style = character_styles.get(character_id, character_styles["xiyang"])
        
        # 构建增强提示词
        enhanced_parts = []
        
        # 1. 用户原始描述
        enhanced_parts.append(user_prompt)
        
        # 2. 添加角色风格
        enhanced_parts.append(f"风格：{char_style['style']}")
        enhanced_parts.append(f"色调：{char_style['color_tone']}")
        enhanced_parts.append(f"氛围：{char_style['mood']}")
        
        # 3. 添加质量和风格偏好
        if style_preference:
            enhanced_parts.append(f"特殊风格：{style_preference}")
        
        # 4. 通用质量增强
        enhanced_parts.extend([
            "高质量，精美细节，专业摄影级别",
            "清晰锐利，色彩鲜艳，构图优美",
            "4K高清，细节丰富"
        ])
        
        # 5. 组合提示词
        enhanced_prompt = ", ".join(enhanced_parts)
        
        # 6. 长度控制（DALL-E有长度限制）
        if len(enhanced_prompt) > 1000:
            enhanced_prompt = enhanced_prompt[:1000] + "..."
        
        return enhanced_prompt
    
    async def _download_and_encode_image(self, image_url: str) -> Optional[str]:
        """
        下载图片并转换为base64编码
        
        Args:
            image_url: 图片URL
            
        Returns:
            base64编码的图片数据
        """
        try:
            print(f"📥 下载图片: {image_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                        print(f"✅ 图片下载完成，大小: {len(image_data)} 字节")
                        return image_base64
                    else:
                        print(f"❌ 图片下载失败: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ 图片下载异常: {e}")
            return None
    
    def should_generate_image(self, user_message: str) -> bool:
        """
        判断是否应该生成图片
        
        Args:
            user_message: 用户消息
            
        Returns:
            是否应该生成图片
        """
        image_keywords = [
            "画", "画个", "画一个", "画一张", "画出",
            "图", "图片", "生成图", "来张图", "来个图",
            "画画", "绘制", "制作图片", "做张图",
            "想看", "给我看看", "展示一下",
            "创作", "设计", "描绘",
            "draw", "paint", "image", "picture", "show me"
        ]
        
        user_message_lower = user_message.lower()
        return any(keyword in user_message_lower for keyword in image_keywords)
    
    def extract_image_description(self, user_message: str) -> str:
        """
        从用户消息中提取图片描述
        
        Args:
            user_message: 用户消息
            
        Returns:
            提取的图片描述
        """
        # 移除图片生成相关的触发词
        trigger_words = ["画", "画个", "画一个", "画一张", "生成图", "来张图", "给我"]
        
        description = user_message
        for word in trigger_words:
            description = description.replace(word, "").strip()
        
        # 如果描述太短，返回原始消息
        if len(description) < 3:
            description = user_message
        
        return description
    
    async def get_character_image_response(
        self, 
        character_id: str, 
        image_result: Dict[str, Any]
    ) -> str:
        """
        根据角色生成对图片的回应
        
        Args:
            character_id: 角色ID
            image_result: 图片生成结果
            
        Returns:
            角色的回应文本
        """
        if not image_result.get("success"):
            # 图片生成失败的回应
            responses = {
                "xiyang": "爸妈，抱歉，图片生成遇到了一些技术问题，我来帮您想想其他方式。",
                "meiyang": "爸爸妈妈，呀，图片没有生成成功呢，让我再试试别的方法~",
                "lanyang": "爷爷奶奶，哎呀，图片没画出来，可能是我描述得不够好！"
            }
            return responses.get(character_id, "图片生成失败了，请稍后再试。")
        
        # 图片生成成功的回应
        success_responses = {
            "xiyang": "爸妈，我按您的要求画了这张图，希望您喜欢！",
            "meiyang": "爸爸妈妈，我给你们画了这张图片，怎么样？温馨吗？",
            "lanyang": "爷爷奶奶！我画了一张超级棒的图给你们看，快看快看！"
        }
        
        return success_responses.get(character_id, "图片已经为您生成好了！")


# 创建全局实例
image_service = ImageService()
