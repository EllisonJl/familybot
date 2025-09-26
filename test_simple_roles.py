#!/usr/bin/env python3
"""
简化的角色测试 - 直接测试角色特性
"""

import sys
import os
sys.path.append('/Users/jllulu/Desktop/familybot/ai_agent')

# 直接导入AI Agent模块
from agents.character_agent import CharacterManager

def test_character_responses():
    """测试三个角色的不同回复风格"""
    print("🚀 开始测试三个角色的个性化回复...")
    
    # 初始化角色管理器
    character_manager = CharacterManager()
    
    # 测试消息
    test_messages = [
        {
            "user_input": "我今天感觉有点累，工作很辛苦。",
            "context": "关心老人身体健康"
        },
        {
            "user_input": "天气变冷了，我担心会感冒。",
            "context": "关心老人保暖"
        },
        {
            "user_input": "最近睡眠不太好，经常失眠。",
            "context": "关心老人睡眠质量"
        }
    ]
    
    # 角色列表
    characters = [
        {"id": "xiyang", "name": "喜羊羊（儿子）"},
        {"id": "meiyang", "name": "美羊羊（女儿）"},
        {"id": "lanyang", "name": "懒羊羊（孙子）"}
    ]
    
    # 测试每个角色对每条消息的回复
    for i, message_data in enumerate(test_messages, 1):
        user_input = message_data["user_input"]
        context = message_data["context"]
        
        print(f"\n{'='*60}")
        print(f"📝 测试消息 {i}: {user_input}")
        print(f"🎯 场景: {context}")
        print(f"{'='*60}")
        
        for character in characters:
            character_id = character["id"]
            character_name = character["name"]
            
            print(f"\n🎭 {character_name} 的回复:")
            
            try:
                # 获取角色代理
                agent = character_manager.get_agent(character_id)
                if agent:
                    # 生成回复
                    response = agent.generate_response(user_input, context={})
                    print(f"💬 {response['content']}")
                    print(f"😊 情感: {response['emotion']}")
                    print(f"🎨 风格: {response['style']}")
                else:
                    print(f"❌ 未找到角色: {character_id}")
                    
            except Exception as e:
                print(f"❌ 生成回复时出错: {str(e)}")
        
        print("\n" + "-"*40)

def test_character_greetings():
    """测试角色问候语"""
    print(f"\n{'='*60}")
    print("🎉 测试角色问候语")
    print(f"{'='*60}")
    
    character_manager = CharacterManager()
    
    characters = [
        {"id": "xiyang", "name": "喜羊羊（儿子）"},
        {"id": "meiyang", "name": "美羊羊（女儿）"},
        {"id": "lanyang", "name": "懒羊羊（孙子）"}
    ]
    
    for character in characters:
        character_id = character["id"]
        character_name = character["name"]
        
        print(f"\n🎭 {character_name}:")
        
        try:
            agent = character_manager.get_agent(character_id)
            if agent:
                greeting = agent.get_greeting()
                print(f"👋 问候语: {greeting}")
                
                # 获取角色配置信息
                config = agent.config
                print(f"👤 角色: {config.get('role', '未知')}")
                print(f"🎨 性格: {config.get('personality', '未知')}")
                print(f"🔊 语音: {config.get('voice', '未知')}")
            else:
                print(f"❌ 未找到角色: {character_id}")
                
        except Exception as e:
            print(f"❌ 获取问候语时出错: {str(e)}")

def main():
    try:
        # 测试问候语
        test_character_greetings()
        
        # 测试对话回复
        test_character_responses()
        
        print(f"\n{'='*60}")
        print("✅ 角色测试完成！")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

