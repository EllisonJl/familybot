#!/usr/bin/env python3
"""
测试三个角色的聊天功能
"""

import requests
import json
import time

# 配置
AI_AGENT_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:8081/api/v1"

def test_ai_agent_direct(character_id, character_name, message, user_role="elderly"):
    """直接测试AI Agent"""
    print(f"\n🧪 测试 {character_name} (直接AI Agent)")
    print(f"💬 用户消息: {message}")
    
    try:
        response = requests.post(
            f"{AI_AGENT_URL}/chat",
            json={
                "message": message,
                "user_id": "test-user",
                "character_id": character_id,
                "role": user_role
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 {data['character_name']} 回复: {data['response']}")
            print(f"😊 情感: {data['emotion']}")
            return True
        else:
            print(f"❌ AI Agent错误: {response.status_code} - {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ AI Agent超时")
        return False
    except Exception as e:
        print(f"❌ AI Agent异常: {str(e)}")
        return False

def test_backend_api(character_id, character_name, message, user_role="elderly"):
    """通过后端API测试"""
    print(f"\n🧪 测试 {character_name} (通过后端API)")
    print(f"💬 用户消息: {message}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "userId": "test-user",
                "characterId": character_id,
                "message": message,
                "useAgent": True,
                "role": user_role
            },
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:8080"
            },
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 {data['characterName']} 回复: {data.get('aiResponseText', data.get('response', '无回复'))}")
            print(f"😊 情感: {data.get('emotion', '未知')}")
            print(f"📊 状态: {data.get('status', 'UNKNOWN')}")
            if data.get('error'):
                print(f"⚠️  错误信息: {data['error']}")
            return True
        else:
            print(f"❌ 后端错误: {response.status_code} - {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ 后端超时")
        return False
    except Exception as e:
        print(f"❌ 后端异常: {str(e)}")
        return False

def main():
    print("🚀 开始测试三个角色的聊天功能...")
    
    # 测试数据
    test_cases = [
        {
            "character_id": "xiyang",
            "character_name": "喜羊羊（儿子）",
            "messages": [
                "儿子，我今天感觉有点累，你工作怎么样？",
                "你最近有没有好好吃饭？妈妈很担心你。",
                "记得按时休息，不要太拼命了。"
            ]
        },
        {
            "character_id": "meiyang", 
            "character_name": "美羊羊（女儿）",
            "messages": [
                "女儿，妈妈想你了，你在外面还好吗？",
                "天气凉了，记得多穿衣服。",
                "什么时候回家看看爸爸妈妈？"
            ]
        },
        {
            "character_id": "lanyang",
            "character_name": "懒羊羊（孙子）", 
            "messages": [
                "小宝贝，爷爷奶奶想你啦！",
                "在学校有没有听老师的话？",
                "周末想吃什么？爷爷给你做。"
            ]
        }
    ]
    
    # 等待服务完全启动
    print("⏳ 等待服务启动...")
    time.sleep(5)
    
    # 测试每个角色
    for test_case in test_cases:
        character_id = test_case["character_id"]
        character_name = test_case["character_name"]
        messages = test_case["messages"]
        
        print(f"\n{'='*60}")
        print(f"🎭 开始测试角色: {character_name}")
        print(f"{'='*60}")
        
        # 测试第一条消息（AI Agent直接）
        if len(messages) > 0:
            success = test_ai_agent_direct(character_id, character_name, messages[0])
            time.sleep(2)  # 间隔
        
        # 测试第二条消息（后端API）
        if len(messages) > 1:
            success = test_backend_api(character_id, character_name, messages[1])
            time.sleep(2)  # 间隔
        
        # 测试第三条消息（AI Agent直接）
        if len(messages) > 2:
            success = test_ai_agent_direct(character_id, character_name, messages[2])
            time.sleep(2)  # 间隔
    
    print(f"\n{'='*60}")
    print("✅ 测试完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

