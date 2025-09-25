#!/usr/bin/env python3
"""
AI Agent功能测试脚本
测试AI Agent处理老人对话的能力
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_agent'))

from models.state import ConversationState
from agents.character_agent import CharacterAgent
from datetime import datetime

def test_elder_conversation():
    """测试老人对话场景"""
    
    print("🤖 启动AI Agent测试...")
    print("=" * 50)
    
    # 测试场景1：关心身体健康 - 喜羊羊
    print("\n📍 测试场景1：老人关心身体健康 (喜羊羊)")
    print("-" * 40)
    
    try:
        xiyang_agent = CharacterAgent("xiyang")
        state1 = ConversationState(
            user_id="test_elder_001",
            timestamp=datetime.now().isoformat(),
            user_input="唉，最近老是腰疼，晚上睡不好觉，你说我这老毛病该怎么办啊？",
            selected_character="xiyang"
        )
        
        response1 = xiyang_agent.generate_response(state1.user_input)
        print(f"👴 老人说：{state1.user_input}")
        print(f"🐑 喜羊羊回复：{response1.get('response', '抱歉，我无法回应')}")
        print(f"😊 情绪识别：{response1.get('emotion', '未知')}")
        print(f"🎯 意图识别：{response1.get('intent', '未知')}")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    
    # 测试场景2：想念家人 - 美羊羊
    print("\n📍 测试场景2：老人想念家人 (美羊羊)")
    print("-" * 40)
    
    try:
        meiyang_agent = CharacterAgent("meiyang")
        state2 = ConversationState(
            user_id="test_elder_001", 
            timestamp=datetime.now().isoformat(),
            user_input="孩子们都在外面打工，好久没回来了，我一个人在家真的很孤单啊...",
            selected_character="meiyang"
        )
        
        response2 = meiyang_agent.generate_response(state2.user_input)
        print(f"👴 老人说：{state2.user_input}")
        print(f"🐑 美羊羊回复：{response2.get('response', '抱歉，我无法回应')}")
        print(f"😊 情绪识别：{response2.get('emotion', '未知')}")
        print(f"🎯 意图识别：{response2.get('intent', '未知')}")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        
    # 测试场景3：日常生活困难 - 懒羊羊
    print("\n📍 测试场景3：日常生活困难 (懒羊羊)")
    print("-" * 40)
    
    try:
        lanyang_agent = CharacterAgent("lanyang")
        state3 = ConversationState(
            user_id="test_elder_001",
            timestamp=datetime.now().isoformat(),
            user_input="手机这个东西太复杂了，我不会用，连个电话都打不出去...",
            selected_character="lanyang"
        )
        
        response3 = lanyang_agent.generate_response(state3.user_input)
        print(f"👴 老人说：{state3.user_input}")
        print(f"🐑 懒羊羊回复：{response3.get('response', '抱歉，我无法回应')}")
        print(f"😊 情绪识别：{response3.get('emotion', '未知')}")
        print(f"🎯 意图识别：{response3.get('intent', '未知')}")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    
    print("\n🎉 AI Agent测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_elder_conversation()
