#!/usr/bin/env python3
"""
图片生成功能测试脚本
测试不同角色的图片生成效果
"""

import requests
import json
import time
import asyncio
from pathlib import Path

# 测试配置
API_BASE_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:8080"

def test_image_keywords():
    """测试图片关键词识别"""
    print("🧪 测试图片关键词识别...")
    
    test_messages = [
        "画一张美丽的日落图片",
        "给我生成一个可爱的小猫图",
        "帮我画个春天的花园",
        "来张图片显示一下家庭聚餐",
        "今天天气不错",  # 不应该触发图片生成
        "draw me a beautiful landscape",
        "show me a picture of happiness"
    ]
    
    for message in test_messages:
        # 模拟图片生成检测逻辑
        image_keywords = [
            "画", "画个", "画一个", "画一张", "画出",
            "图", "图片", "生成图", "来张图", "来个图",
            "画画", "绘制", "制作图片", "做张图",
            "想看", "给我看看", "展示一下",
            "创作", "设计", "描绘",
            "draw", "paint", "image", "picture", "show me"
        ]
        
        should_generate = any(keyword in message.lower() for keyword in image_keywords)
        status = "✅ 应该生成图片" if should_generate else "❌ 不应该生成图片"
        print(f"  '{message}' -> {status}")


def test_character_styles():
    """测试不同角色的风格增强"""
    print("\n🎨 测试角色风格增强...")
    
    characters = {
        "xiyang": "成熟稳重风格，商务风，现代简约",
        "meiyang": "温馨甜美风格，日系风，清新自然", 
        "lanyang": "童趣可爱风格，卡通风，活泼明快"
    }
    
    base_prompt = "一个美丽的花园"
    
    for char_id, style in characters.items():
        print(f"  {char_id}: {base_prompt} + {style}")


async def test_ai_agent_direct():
    """直接测试AI Agent的图片生成"""
    print("\n🤖 测试AI Agent直接调用...")
    
    test_cases = [
        {
            "character_id": "xiyang",
            "message": "画一张春天的花园图片",
            "expected": "应该生成专业风格的花园图片"
        },
        {
            "character_id": "meiyang", 
            "message": "给我画个温馨的家庭聚餐场景",
            "expected": "应该生成温馨甜美风格的聚餐图片"
        },
        {
            "character_id": "lanyang",
            "message": "画个超级可爱的小动物",
            "expected": "应该生成童趣卡通风格的动物图片"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  测试 {i}: {test_case['character_id']} - {test_case['message']}")
        
        payload = {
            "message": test_case["message"],
            "user_id": "test_user",
            "character_id": test_case["character_id"],
            "use_agent": True,
            "voice_config": {
                "voice": "onyx" if test_case["character_id"] == "xiyang" else "nova" if test_case["character_id"] == "meiyang" else "fable",
                "speed": 1.0
            }
        }
        
        try:
            print(f"    📤 发送请求到 {API_BASE_URL}/chat...")
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json=payload,
                timeout=60  # 图片生成可能需要较长时间
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ 响应成功:")
                print(f"      - 回复: {data.get('response', 'N/A')[:100]}...")
                print(f"      - 有图片URL: {'是' if data.get('image_url') else '否'}")
                print(f"      - 有图片Base64: {'是' if data.get('image_base64') else '否'}")
                print(f"      - 图片描述: {data.get('image_description', 'N/A')}")
                print(f"      - 增强提示词: {data.get('enhanced_prompt', 'N/A')[:50]}...")
                
                if data.get('image_url'):
                    print(f"      - 图片URL: {data['image_url']}")
                    
                    # 保存图片URL到文件
                    result_file = Path(f"test_results_{test_case['character_id']}.txt")
                    with open(result_file, "w", encoding="utf-8") as f:
                        f.write(f"角色: {test_case['character_id']}\n")
                        f.write(f"消息: {test_case['message']}\n")
                        f.write(f"回复: {data.get('response', 'N/A')}\n")
                        f.write(f"图片URL: {data.get('image_url', 'N/A')}\n")
                        f.write(f"图片描述: {data.get('image_description', 'N/A')}\n")
                        f.write(f"增强提示词: {data.get('enhanced_prompt', 'N/A')}\n")
                    
                    print(f"      📄 结果已保存到 {result_file}")
                
            else:
                print(f"    ❌ 请求失败: {response.status_code}")
                print(f"      错误信息: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ 请求异常: {e}")
        
        print(f"    ⏳ 等待3秒后继续下一个测试...")
        time.sleep(3)


def test_backend_integration():
    """测试后端集成"""
    print("\n🔗 测试Spring Boot后端集成...")
    
    payload = {
        "userId": "test_user",
        "characterId": "meiyang",
        "message": "画一张温馨的家庭合照",
        "voiceConfig": {
            "voice": "nova",
            "speed": 1.0
        }
    }
    
    try:
        print(f"    📤 发送请求到后端 {BACKEND_URL}/api/v1/chat...")
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ 后端响应成功:")
            print(f"      - 回复: {data.get('aiResponseText', 'N/A')[:100]}...")
            print(f"      - 有图片URL: {'是' if data.get('imageUrl') else '否'}")
            print(f"      - 有图片Base64: {'是' if data.get('imageBase64') else '否'}")
            print(f"      - 图片描述: {data.get('imageDescription', 'N/A')}")
        else:
            print(f"    ❌ 后端请求失败: {response.status_code}")
            print(f"      错误信息: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"    ❌ 后端请求异常: {e}")


def main():
    """主测试流程"""
    print("🎯 开始图片生成功能测试\n")
    
    # 1. 测试关键词识别
    test_image_keywords()
    
    # 2. 测试风格增强
    test_character_styles()
    
    # 3. 测试AI Agent直接调用
    print("\n⏳ 即将开始AI Agent测试，请确保AI Agent服务已启动...")
    time.sleep(2)
    asyncio.run(test_ai_agent_direct())
    
    # 4. 测试后端集成
    print("\n⏳ 即将开始后端集成测试...")
    time.sleep(2)
    test_backend_integration()
    
    print("\n🎉 图片生成功能测试完成!")
    print("\n📋 测试总结:")
    print("  1. ✅ 关键词识别逻辑测试")
    print("  2. ✅ 角色风格增强测试") 
    print("  3. 🧪 AI Agent直接调用测试")
    print("  4. 🧪 后端集成测试")
    print("\n💡 提示:")
    print("  - 请检查生成的图片URL是否可以正常访问")
    print("  - 请验证不同角色的图片风格是否有明显差异")
    print("  - 请确认前端能正确显示生成的图片")


if __name__ == "__main__":
    main()
