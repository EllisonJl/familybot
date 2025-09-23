import os
from dotenv import load_dotenv
from openai import OpenAI

# DashScope 语音模型
from dashscope.audio.tts import SpeechSynthesizer
from dashscope.audio.asr import Transcription

# === 加载 .env 文件 ===
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=dotenv_path, override=True)

# 获取环境变量
api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv("DASHSCOPE_BASE_URL")

if not api_key:
    raise RuntimeError("❌ 未设置 DASHSCOPE_API_KEY，请检查 .env 文件！")

print(f"✅ 当前使用的 API KEY: {repr(api_key)}")

# 创建 DashScope/OpenAI 客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# === 测试 LLM ===
print("\n=== 🧠 测试 Qwen LLM ===")
response = client.chat.completions.create(
    model="qwen3-max-preview",
    messages=[
        {"role": "system", "content": "你是一个友好的 AI 助手"},
        {"role": "user", "content": "你好，请介绍一下你自己"},
    ]
)
print("🤖 LLM 回复:", response.choices[0].message.content)


import dashscope

# ✅ 直接写入你测试成功的 API Key
api_key = "sk-5c523ce367f3486e9bd68f87be0fcabb"

print(f"✅ 当前使用的 API KEY: {repr(api_key)}")

# === 构建 ASR 请求 ===
messages = [
    {
        "role": "system",
        "content": [{"text": ""}]
    },
    {
        "role": "user",
        "content": [
            {"audio": "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3"},
        ]
    }
]

response = dashscope.MultiModalConversation.call(
    api_key=api_key,
    model="qwen3-asr-flash",
    messages=messages,
    result_format="message",
    asr_options={
        "enable_lid": True,
        "enable_itn": False
    }
)

print("\n🧠 ASR 识别结果:")
print(response)


import os
import requests
import dashscope
import pyaudio
import time
import base64
import numpy as np
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=dotenv_path, override=True)

# DashScope 语音模型
from dashscope.audio.tts import SpeechSynthesizer

api_key = os.getenv("DASHSCOPE_API_KEY")

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True)

text = "你好啊，我是通义千问"
response = dashscope.MultiModalConversation.call(
    api_key=api_key,
    model="qwen3-tts-flash",
    text=text,
    voice="Cherry",
    language_type="Chinese",
    stream=True
)

for chunk in response:
    # 打印每个块的内容，以进行调试
    print(f"Received chunk: {chunk}")

    if chunk.output is not None and chunk.output.audio is not None:
        audio = chunk.output.audio
        wav_bytes = base64.b64decode(audio.data)
        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
        # 直接播放音频数据
        stream.write(audio_np.tobytes())
    if chunk.output is not None and chunk.output.finish_reason == "stop":
        print("finish at: {} ", chunk.output.audio.expires_at)

time.sleep(0.8)

stream.stop_stream()
stream.close()
p.terminate()
