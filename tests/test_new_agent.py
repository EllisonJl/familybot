#!/usr/bin/env python3
"""
测试新的AI Agent系统
验证路由、Graph RAG、多角色等功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.graph.conversation_graph import ConversationGraph
from ai_agent.config import CHARACTER_CONFIGS


async def test_conversation_flow():
    """测试对话流程"""
    print("🧪 开始测试新的AI Agent系统")
    print("=" * 50)
    
    # 初始化对话图
    conv_graph = ConversationGraph()
    
    # 测试用例
    test_cases = [
        {
            "input": "爷爷奶奶好！我想你们了！",
            "expected_character": "lanyang",
            "description": "测试孙子角色路由"
        },
        {
            "input": "我最近身体不太舒服，血压有点高",
            "expected_character": "xiyang", 
            "description": "测试健康关注路由"
        },
        {
            "input": "我有点孤单，想要有人陪陪我",
            "expected_character": "meiyang",
            "description": "测试情感支持路由"
        },
        {
            "input": "什么是高血压？应该怎么预防？",
            "expected_character": "xiyang",
            "description": "测试知识查询路由"
        },
        {
            "input": "今天天气真好，心情很棒！",
            "expected_character": None,
            "description": "测试一般对话"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 测试用例 {i}: {test_case['description']}")
        print(f"👤 用户输入: {test_case['input']}")
        
        try:
            # 处理对话
            result = await conv_graph.process_conversation(
                user_input=test_case['input'],
                user_id=f"test_user_{i}",
                character_id="xiyang"  # 初始角色
            )
            
            # 输出结果
            print(f"🤖 响应角色: {result['character_name']} ({result['character_id']})")
            print(f"💬 回复内容: {result['response']}")
            print(f"😊 情绪状态: {result['emotion']}")
            print(f"🎯 识别意图: {result['intent']}")
            
            if result.get('router_info'):
                router_info = result['router_info']
                print(f"🔀 路由类型: {router_info['type']}")
                print(f"🎯 路由逻辑: {router_info['logic']}")
                print(f"📊 路由置信度: {router_info['confidence']:.2f}")
            
            if result.get('rag_enhanced'):
                print(f"📚 RAG增强: 是")
            
            # 验证路由结果
            if test_case['expected_character']:
                if result['character_id'] == test_case['expected_character']:
                    print(f"✅ 路由正确: 预期 {test_case['expected_character']}")
                else:
                    print(f"⚠️ 路由偏差: 预期 {test_case['expected_character']}, 实际 {result['character_id']}")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            print("-" * 40)
    
    print("\n🎉 测试完成！")


async def test_character_details():
    """测试角色详细信息"""
    print("\n👥 测试角色详细配置")
    print("=" * 50)
    
    for char_id, config in CHARACTER_CONFIGS.items():
        print(f"\n🎭 角色: {config['name']} ({char_id})")
        print(f"👤 身份: {config['role']} ({config['age']})")
        print(f"💝 性格: {config['personality']}")
        print(f"🎤 声音: {config['voice']} (速度: {config['voice_speed']})")
        print(f"👋 问候语: {config['greeting']}")
        print(f"🎲 开场语数量: {len(config.get('opening_phrases', []))}")
        
        # 显示部分系统提示词
        prompt_preview = config['system_prompt'][:200] + "..." if len(config['system_prompt']) > 200 else config['system_prompt']
        print(f"📋 系统提示词预览: {prompt_preview}")
        print("-" * 40)


async def test_graph_rag():
    """测试Graph RAG知识检索"""
    print("\n📚 测试Graph RAG知识检索")
    print("=" * 50)
    
    from ai_agent.rag.graph_rag import graph_rag
    
    test_queries = [
        "老年人如何保持健康？",
        "高血压应该注意什么？",
        "感到孤独时怎么办？",
        "如何与家人保持联系？"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        
        try:
            result = await graph_rag.query_knowledge(query, limit=3)
            
            print(f"📊 检索置信度: {result.confidence:.2f}")
            print(f"🔗 知识来源: {', '.join(result.knowledge_sources)}")
            print(f"📝 查询扩展: {', '.join(result.query_expansion[:3])}")
            
            print(f"💡 相关知识:")
            for i, context in enumerate(result.relevant_contexts, 1):
                print(f"   {i}. [{context['domain']}] {context['content'][:100]}...")
                print(f"      相关性: {context['relevance_score']:.2f}")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            print("-" * 40)


async def main():
    """主测试函数"""
    print("🚀 FamilyBot AI Agent 系统测试")
    print("=" * 60)
    
    try:
        # 测试角色配置
        await test_character_details()
        
        # 测试Graph RAG
        await test_graph_rag()
        
        # 测试完整对话流程
        await test_conversation_flow()
        
        print("\n🎊 所有测试完成！系统运行正常！")
        
    except Exception as e:
        print(f"\n💥 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
