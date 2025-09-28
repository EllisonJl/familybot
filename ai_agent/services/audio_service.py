"""
音频服务模块 - 统一管理ASR和TTS功能
支持多种音频格式，提供流式和批量处理接口
"""

import os
import base64
import io
import tempfile
import requests
from typing import Optional, Dict, Any, Union, AsyncGenerator
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from openai import OpenAI
import asyncio

from config import Config


class AudioService:
    """音频处理服务类"""
    
    def __init__(self):
        """初始化音频服务"""
        self.api_key = Config.DASHSCOPE_API_KEY
        self.sample_rate = Config.SAMPLE_RATE
        self.channels = Config.CHANNELS
        
        # 初始化OpenAI客户端
        if Config.USE_OPENAI_TTS:
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            print(f"✅ OpenAI TTS客户端初始化完成")
        
        # 支持的音频格式
        self.supported_formats = ['wav', 'mp3', 'm4a', 'flac', 'ogg']
        
        print(f"✅ 音频服务初始化完成 - 采样率: {self.sample_rate}, 声道: {self.channels}")
    
    def convert_audio_format(
        self, 
        audio_data: bytes, 
        source_format: str, 
        target_format: str = 'wav'
    ) -> bytes:
        """
        转换音频格式
        
        Args:
            audio_data: 原始音频数据
            source_format: 源格式
            target_format: 目标格式
            
        Returns:
            转换后的音频数据
        """
        try:
            # 使用pydub进行格式转换
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data), 
                format=source_format
            )
            
            # 统一采样率和声道
            audio = audio.set_frame_rate(self.sample_rate)
            audio = audio.set_channels(self.channels)
            
            # 导出为目标格式
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format=target_format)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            print(f"❌ 音频格式转换失败: {e}")
            raise
    
    def prepare_audio_for_asr(self, audio_data: bytes, source_format: str = 'wav') -> str:
        """
        为ASR准备音频数据
        
        Args:
            audio_data: 音频数据
            source_format: 源格式
            
        Returns:
            base64编码的音频数据
        """
        try:
            # 转换为wav格式
            if source_format != 'wav':
                audio_data = self.convert_audio_format(audio_data, source_format, 'wav')
            
            # base64编码
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return audio_base64
            
        except Exception as e:
            print(f"❌ ASR音频准备失败: {e}")
            raise
    
    async def speech_to_text(
        self, 
        audio_data: Union[bytes, str], 
        source_format: str = 'wav',
        language: str = 'zh'
    ) -> Dict[str, Any]:
        """
        语音转文字 (ASR)
        
        Args:
            audio_data: 音频数据（bytes）或base64字符串
            source_format: 音频格式
            language: 语言代码
            
        Returns:
            识别结果
        """
        try:
            # 处理音频数据
            if isinstance(audio_data, bytes):
                audio_base64 = self.prepare_audio_for_asr(audio_data, source_format)
            else:
                audio_base64 = audio_data
            
            # 构建ASR请求
            messages = [
                {
                    "role": "system",
                    "content": [{"text": ""}]
                },
                {
                    "role": "user",
                    "content": [
                        {"audio": f"data:audio/wav;base64,{audio_base64}"},
                    ]
                }
            ]
            
            # 调用DashScope ASR API
            response = dashscope.MultiModalConversation.call(
                api_key=self.api_key,
                model=Config.ASR_MODEL,
                messages=messages,
                result_format="message",
                asr_options={
                    "enable_lid": True,  # 语言识别
                    "enable_itn": True   # 数字转换
                }
            )
            
            if response.status_code == 200:
                # 提取识别结果
                result_text = ""
                if hasattr(response, 'output') and hasattr(response.output, 'choices'):
                    if len(response.output.choices) > 0:
                        choice = response.output.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                            result_text = choice.message.content
                
                return {
                    "success": True,
                    "text": result_text,
                    "language": language,
                    "confidence": 1.0,  # DashScope不提供置信度
                    "duration": 0  # 暂无持续时间信息
                }
            else:
                return {
                    "success": False,
                    "error": f"ASR API调用失败: {response.message}",
                    "text": ""
                }
                
        except Exception as e:
            print(f"❌ 语音识别失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    async def text_to_speech(
        self, 
        text: str, 
        voice: str,  # 移除默认值，强制传入音色参数
        speed: float = 1.0,
        stream: bool = False
    ) -> Union[bytes, AsyncGenerator[bytes, None]]:
        """
        文字转语音 (TTS)
        
        Args:
            text: 要合成的文本
            voice: 声音类型
            speed: 语速倍率
            stream: 是否流式返回
            
        Returns:
            音频数据或音频流
        """
        try:
            if stream:
                return self._text_to_speech_stream(text, voice, speed)
            else:
                return await self._text_to_speech_batch(text, voice, speed)
                
        except Exception as e:
            print(f"❌ 语音合成失败: {e}")
            raise
    
    async def _generate_xiyang_voice(self, text: str, speed: float) -> bytes:
        """喜羊羊专用TTS - 深沉男声onyx"""
        print(f"🎭 生成喜羊羊声音 - voice=onyx, text={text[:20]}...")
        response = self.openai_client.audio.speech.create(
            model=Config.TTS_MODEL,
            voice="onyx",  # 固定使用onyx深沉男声
            input=text,
            speed=speed
        )
        audio_data = response.content
        print(f"✅ 喜羊羊TTS成功，生成 {len(audio_data)} 字节音频数据")
        return audio_data
    
    async def _generate_meiyang_voice(self, text: str, speed: float) -> bytes:
        """美羊羊专用TTS - 优雅女声nova"""
        print(f"🌸 生成美羊羊声音 - voice=nova, text={text[:20]}...")
        response = self.openai_client.audio.speech.create(
            model=Config.TTS_MODEL,
            voice="nova",  # 固定使用nova优雅女声
            input=text,
            speed=speed
        )
        audio_data = response.content
        print(f"✅ 美羊羊TTS成功，生成 {len(audio_data)} 字节音频数据")
        return audio_data
    
    async def _generate_lanyang_voice(self, text: str, speed: float) -> bytes:
        """懒羊羊专用TTS - 英国口音fable"""
        print(f"🇬🇧 生成懒羊羊声音 - voice=fable, text={text[:20]}...")
        response = self.openai_client.audio.speech.create(
            model=Config.TTS_MODEL,
            voice="fable",  # 固定使用fable英国口音
            input=text,
            speed=speed
        )
        audio_data = response.content
        print(f"✅ 懒羊羊TTS成功，生成 {len(audio_data)} 字节音频数据")
        return audio_data

    async def generate_character_voice(self, character_id: str, text: str, speed: float = 1.0) -> bytes:
        """根据角色ID生成专用声音"""
        print(f"🎯 根据角色ID选择专用TTS - character_id={character_id}")
        
        if character_id == "xiyang":
            return await self._generate_xiyang_voice(text, speed)
        elif character_id == "meiyang":
            return await self._generate_meiyang_voice(text, speed)
        elif character_id == "lanyang":
            return await self._generate_lanyang_voice(text, speed)
        else:
            # 默认使用onyx声音
            print(f"⚠️ 未知角色ID {character_id}，使用默认onyx声音")
            return await self._generate_xiyang_voice(text, speed)

    async def _text_to_speech_batch(
        self, 
        text: str, 
        voice: str, 
        speed: float
    ) -> bytes:
        """批量TTS处理 - 使用角色专用TTS函数"""
        try:
            # 如果启用了OpenAI TTS，根据voice参数选择专用函数
            if Config.USE_OPENAI_TTS:
                print(f"🎵 选择角色专用TTS函数 - voice={voice}")
                
                # 根据voice参数调用对应的专用函数
                if voice == "onyx":
                    return await self._generate_xiyang_voice(text, speed)
                elif voice == "nova":  # 美羊羊现在使用nova音色
                    return await self._generate_meiyang_voice(text, speed)
                elif voice == "fable":
                    return await self._generate_lanyang_voice(text, speed)
                else:
                    # 默认情况下使用通用方法
                    print(f"🎵 使用通用OpenAI TTS - model={Config.TTS_MODEL}, voice={voice}, text={text[:20]}...")
                    response = self.openai_client.audio.speech.create(
                        model=Config.TTS_MODEL,
                        voice=voice,
                        input=text,
                        speed=speed
                    )
                    audio_data = response.content
                    print(f"✅ 通用OpenAI TTS成功，生成 {len(audio_data)} 字节音频数据")
                    return audio_data
            
            # 如果使用DashScope（保留原有逻辑作为备份）
            else:
                import dashscope
                from dashscope.audio.tts import SpeechSynthesizer
                
                # 设置API key
                dashscope.api_key = self.api_key
                
                response = SpeechSynthesizer.call(
                    model=Config.TTS_MODEL,
                    text=text,
                    voice=voice,
                    sample_rate=24000,
                    format='wav'
                )
                
                print(f"🎵 DashScope TTS调用参数: model={Config.TTS_MODEL}, voice={voice}, text={text[:20]}...")
                
                # DashScope SDK返回的是SpeechSynthesisResult对象，不是HTTP响应
                if hasattr(response, 'get_audio_data'):
                    # 检查响应状态
                    api_response = response.get_response()
                    print(f"🔍 API响应: {api_response}")
                    
                    # 直接获取音频数据
                    audio_data = response.get_audio_data()
                    if audio_data:
                        print(f"✅ DashScope TTS成功，生成 {len(audio_data)} 字节音频数据")
                        return audio_data
                    else:
                        print("⚠️ 响应成功但无音频数据")
                else:
                    # 记录详细错误信息
                    print(f"🔍 TTS响应结构: {type(response)}")
                    print(f"🔍 response属性: {dir(response)}")
                    
                    if hasattr(response, 'output'):
                        print(f"🔍 output类型: {type(response.output)}")
                        print(f"🔍 output属性: {dir(response.output)}") 
                    
                        if hasattr(response.output, 'audio'):
                            print(f"🔍 audio类型: {type(response.output.audio)}")
                            print(f"🔍 audio内容: {response.output.audio}")
                        
                        # 尝试不同的访问方式
                        if isinstance(response.output.audio, dict):
                            if 'url' in response.output.audio:
                                audio_url = response.output.audio['url']
                                print(f"✅ 使用字典方式获得URL: {audio_url}")
                                
                                # 下载音频数据
                                import requests
                                audio_response = requests.get(audio_url)
                                audio_response.raise_for_status()
                                
                                audio_data = audio_response.content
                                print(f"✅ 音频下载成功: {len(audio_data)}字节")
                                return audio_data
                            
                        elif 'data' in response.output.audio:
                            # 直接返回Base64数据
                            audio_data = base64.b64decode(response.output.audio['data'])
                            print(f"✅ 使用Base64数据: {len(audio_data)}字节")
                            return audio_data
                    
                    elif hasattr(response.output.audio, 'url'):
                        audio_url = response.output.audio.url
                        print(f"✅ 使用属性方式获得URL: {audio_url}")
                        
                        # 下载音频数据
                        audio_response = requests.get(audio_url)
                        audio_response.raise_for_status()
                        
                        audio_data = audio_response.content
                        print(f"✅ 音频下载成功: {len(audio_data)}字节")
                        return audio_data
            
            raise Exception(f"TTS响应格式错误: 无法解析音频数据 - 响应: {response}")
                
        except Exception as e:
            print(f"❌ TTS处理失败: {e}")
            print(f"❌ 错误类型: {type(e)}")
            print(f"❌ 错误详情: {str(e)}")
            raise
    
    async def _text_to_speech_stream(
        self, 
        text: str, 
        voice: str, 
        speed: float
    ) -> AsyncGenerator[bytes, None]:
        """流式TTS处理 - 使用qwen3-tts-flash-realtime模型"""
        try:
            # 流式模式使用SpeechSynthesizer
            from dashscope.audio.qwen_tts import SpeechSynthesizer
            
            response = SpeechSynthesizer.call(
                model=Config.TTS_MODEL,
                api_key=self.api_key,
                text=text,
                voice=voice,
                language_type="Chinese",
                stream=True
            )
            
            for chunk in response:
                if (hasattr(chunk, 'output') and 
                    hasattr(chunk.output, 'audio') and 
                    chunk.output.audio is not None):
                    
                    if hasattr(chunk.output.audio, 'data'):
                        # 流式数据直接返回
                        audio_data = base64.b64decode(chunk.output.audio.data)
                        yield audio_data
                    elif hasattr(chunk.output.audio, 'url'):
                        # 如果流式返回URL，下载并返回
                        audio_url = chunk.output.audio.url
                        audio_response = requests.get(audio_url)
                        audio_response.raise_for_status()
                        yield audio_response.content
                    
                if (hasattr(chunk, 'output') and 
                    hasattr(chunk.output, 'finish_reason') and 
                    chunk.output.finish_reason == "stop"):
                    break
                    
        except Exception as e:
            print(f"❌ 流式TTS处理失败: {e}")
            raise
    
    def save_audio_to_file(
        self, 
        audio_data: bytes, 
        file_path: str, 
        audio_format: str = 'wav'
    ):
        """
        保存音频到文件
        
        Args:
            audio_data: 音频数据
            file_path: 文件路径
            audio_format: 音频格式
        """
        try:
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            
            print(f"✅ 音频已保存到: {file_path}")
            
        except Exception as e:
            print(f"❌ 保存音频文件失败: {e}")
            raise
    
    def load_audio_from_file(self, file_path: str) -> bytes:
        """
        从文件加载音频
        
        Args:
            file_path: 文件路径
            
        Returns:
            音频数据
        """
        try:
            with open(file_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            print(f"❌ 加载音频文件失败: {e}")
            raise
    
    def get_audio_info(self, audio_data: bytes, audio_format: str = 'wav') -> Dict[str, Any]:
        """
        获取音频信息
        
        Args:
            audio_data: 音频数据
            audio_format: 音频格式
            
        Returns:
            音频信息
        """
        try:
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data), 
                format=audio_format
            )
            
            return {
                "duration": len(audio) / 1000.0,  # 秒
                "frame_rate": audio.frame_rate,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "format": audio_format
            }
            
        except Exception as e:
            print(f"❌ 获取音频信息失败: {e}")
            return {}
    
    async def test_audio_pipeline(self, test_text: str = "你好，我是FamilyBot测试语音。") -> bool:
        """
        测试音频处理管道
        
        Args:
            test_text: 测试文本
            
        Returns:
            测试是否成功
        """
        try:
            print(f"🧪 开始测试音频管道...")
            
            # 测试TTS
            print(f"📢 测试TTS: {test_text}")
            audio_data = await self.text_to_speech(test_text)
            
            if not audio_data:
                print("❌ TTS测试失败")
                return False
            
            print(f"✅ TTS成功，生成 {len(audio_data)} 字节音频数据")
            
            # 获取音频信息
            audio_info = self.get_audio_info(audio_data)
            print(f"🎵 音频信息: {audio_info}")
            
            # 测试ASR（使用生成的音频）
            print(f"🎙️ 测试ASR...")
            asr_result = await self.speech_to_text(audio_data)
            
            if asr_result["success"]:
                print(f"✅ ASR成功: {asr_result['text']}")
                return True
            else:
                print(f"❌ ASR失败: {asr_result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ 音频管道测试失败: {e}")
            return False


# 全局音频服务实例
audio_service = AudioService()
