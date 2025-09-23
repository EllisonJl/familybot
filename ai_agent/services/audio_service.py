"""
音频服务模块 - 统一管理ASR和TTS功能
支持多种音频格式，提供流式和批量处理接口
"""

import os
import base64
import io
import tempfile
from typing import Optional, Dict, Any, Union, AsyncGenerator
import numpy as np
import soundfile as sf
from pydub import AudioSegment
import dashscope
from dashscope.audio.tts import SpeechSynthesizer
import asyncio

from ..config import Config


class AudioService:
    """音频处理服务类"""
    
    def __init__(self):
        """初始化音频服务"""
        self.api_key = Config.DASHSCOPE_API_KEY
        self.sample_rate = Config.SAMPLE_RATE
        self.channels = Config.CHANNELS
        
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
        voice: str = "Cherry",
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
    
    async def _text_to_speech_batch(
        self, 
        text: str, 
        voice: str, 
        speed: float
    ) -> bytes:
        """批量TTS处理"""
        try:
            response = dashscope.MultiModalConversation.call(
                api_key=self.api_key,
                model=Config.TTS_MODEL,
                text=text,
                voice=voice,
                language_type="Chinese",
                stream=False
            )
            
            if hasattr(response, 'output') and hasattr(response.output, 'audio'):
                audio_data = response.output.audio.data
                return base64.b64decode(audio_data)
            else:
                raise Exception("TTS响应中没有音频数据")
                
        except Exception as e:
            print(f"❌ 批量TTS处理失败: {e}")
            raise
    
    async def _text_to_speech_stream(
        self, 
        text: str, 
        voice: str, 
        speed: float
    ) -> AsyncGenerator[bytes, None]:
        """流式TTS处理"""
        try:
            response = dashscope.MultiModalConversation.call(
                api_key=self.api_key,
                model=Config.TTS_MODEL,
                text=text,
                voice=voice,
                language_type="Chinese",
                stream=True
            )
            
            for chunk in response:
                if (hasattr(chunk, 'output') and 
                    hasattr(chunk.output, 'audio') and 
                    chunk.output.audio is not None):
                    
                    audio_data = base64.b64decode(chunk.output.audio.data)
                    yield audio_data
                    
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
