#!/usr/bin/env python3
"""
简单测试AI Agent的核心功能
"""

import sys
import os
import asyncio
sys.path.append('/Users/jllulu/Desktop/familybot/ai_agent')

async def test_simple_response():
    """测试简单的角色回复生成"""
    try:
        from agents.character_agent import CharacterManager
        from models.state import ConversationState
        
        print("🧪 测试角色管理器...")
        
        # 初始化角色管理器
        character_manager = CharacterManager()
        
        # 获取喜羊羊角色
        xiyang_agent = character_manager.get_agent("xiyang")
        if not xiyang_agent:
            print("❌ 无法获取喜羊羊角色")
            return
        
        print("✅ 成功获取喜羊羊角色")
        
        # 测试生成回复
        user_input = "儿子我今天腰疼的厉害你能给我一点建议吗"
        print(f"💬 用户输入: {user_input}")
        
        # 直接调用角色生成方法
        response = xiyang_agent.generate_response(user_input)
        print(f"🤖 角色回复: {response}")
        
        return response
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_conversation_state():
    """测试对话状态创建"""
    try:
        from models.state import ConversationState
        from datetime import datetime
        
        print("🧪 测试对话状态创建...")
        
        state = ConversationState(
            user_id="test-user",
            user_input="儿子我今天腰疼的厉害你能给我一点建议吗",
            selected_character="xiyang",
            role="elderly",
            timestamp=datetime.now().isoformat(),
            messages=[],
            context={},
            memory_context={},
            rag_context=[],
            voice_config={}
        )
        
        print("✅ 对话状态创建成功")
        print(f"📝 状态: {state.user_input}")
        print(f"🎭 角色: {state.selected_character}")
        print(f"👤 用户角色: {state.role}")
        
        return state
        
    except Exception as e:
        print(f"❌ 状态创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 开始AI Agent核心功能测试...")
    
    # 测试角色回复
    print("\n" + "="*50)
    print("测试1: 角色回复生成")
    print("="*50)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result1 = loop.run_until_complete(test_simple_response())
        if result1:
            print("✅ 角色回复测试成功")
        else:
            print("❌ 角色回复测试失败")
    except Exception as e:
        print(f"❌ 角色回复测试异常: {e}")
    
    # 测试对话状态
    print("\n" + "="*50)
    print("测试2: 对话状态创建")
    print("="*50)
    
    try:
        result2 = loop.run_until_complete(test_conversation_state())
        if result2:
            print("✅ 对话状态测试成功")
        else:
            print("❌ 对话状态测试失败")
    except Exception as e:
        print(f"❌ 对话状态测试异常: {e}")
    
    loop.close()
    
    print("\n" + "="*50)
    print("🎯 测试总结")
    print("="*50)
    print("如果两个测试都成功，说明核心组件正常")
    print("问题可能出在LangGraph的图执行或异步处理上")

if __name__ == "__main__":
    main()

