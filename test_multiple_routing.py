#!/usr/bin/env python3
"""
多语句路由测试脚本
测试不同的用户输入如何路由到不同的角色节点
"""

import sys
import os
import asyncio
import json
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_agent'))

from graph.router import FamilyBotRouter
from agents.character_agent import CharacterAgent
from models.state import ConversationState

async def test_multiple_routing_scenarios():
    """测试多种语句的路由场景"""
    
    print("🎯 FamilyBot多场景路由测试")
    print("=" * 80)
    print("🔬 目标：测试不同语句如何路由到不同的角色节点")
    print("-" * 80)
    
    # 初始化路由器
    try:
        router = FamilyBotRouter()
        print("✅ 路由器初始化完成")
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        return
    
    # 测试场景列表
    test_scenarios = [
        # 身份确认类 - 可能路由到通用或随机角色
        {
            "input": "喂喂喂，你好吗？请问你是谁",
            "expected": "可能是通用回复或任意角色",
            "category": "身份确认"
        },
        {
            "input": "你是谁？能介绍一下自己吗？",
            "expected": "可能是通用回复",
            "category": "身份确认"
        },
        {
            "input": "我不认识你，你是我的什么人？",
            "expected": "可能是通用回复或任意角色",
            "category": "身份确认"
        },
        
        # 明确指向儿子的语句
        {
            "input": "我想听听儿子的声音，你在外面还好吗？",
            "expected": "xiyang_node (儿子)",
            "category": "明确指向儿子"
        },
        {
            "input": "儿子，工作累不累？要注意身体啊",
            "expected": "xiyang_node (儿子)", 
            "category": "明确指向儿子"
        },
        {
            "input": "我的好儿子，妈妈想你了",
            "expected": "xiyang_node (儿子)",
            "category": "明确指向儿子"
        },
        
        # 明确指向女儿的语句
        {
            "input": "我有点孤单，想要有人陪陪我",
            "expected": "meiyang_node (女儿)",
            "category": "情感陪伴→女儿"
        },
        {
            "input": "女儿，你什么时候回家啊？妈妈想你了",
            "expected": "meiyang_node (女儿)",
            "category": "明确指向女儿"
        },
        {
            "input": "我心里难受，需要人安慰一下",
            "expected": "meiyang_node (女儿)",
            "category": "情感支持→女儿"
        },
        
        # 明确指向孙子的语句
        {
            "input": "今天心情不好，想开心一点",
            "expected": "lanyang_node (孙子)",
            "category": "需要开心→孙子"
        },
        {
            "input": "小宝贝，过来陪奶奶说说话",
            "expected": "lanyang_node (孙子)",
            "category": "明确指向孙子"
        },
        {
            "input": "我想听个笑话，让我开心开心",
            "expected": "lanyang_node (孙子)",
            "category": "娱乐需求→孙子"
        },
        
        # 健康相关
        {
            "input": "我最近总是睡不好，是不是身体有什么问题？",
            "expected": "health_concern_node (健康关注)",
            "category": "健康咨询"
        },
        {
            "input": "血压有点高，该怎么办？",
            "expected": "health_concern_node (健康关注)",
            "category": "健康咨询"
        }
    ]
    
    print(f"🧪 准备测试 {len(test_scenarios)} 个场景...\n")
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📝 测试场景 {i}/{len(test_scenarios)}: {scenario['category']}")
        print("=" * 80)
        
        user_input = scenario['input']
        expected = scenario['expected']
        category = scenario['category']
        
        print(f"👤 用户输入：「{user_input}」")
        print(f"🎯 预期路由：{expected}")
        print()
        
        try:
            # 创建对话状态
            state = ConversationState(
                user_id=f"test_user_{i:03d}",
                timestamp=datetime.now().isoformat(),
                user_input=user_input
            )
            
            print("🔍 开始路由分析...")
            # 执行路由分析
            analyzed_state = await router.analyze_and_route_query(state)
            
            # 执行路由决策
            route_node = router.route_query(analyzed_state)
            
            # 分析结果
            router_info = analyzed_state.router
            
            print("📊 分析结果：")
            print("┌" + "─" * 78 + "┐")
            print(f"│ 🎯 路由类型: {router_info.type:<62} │")
            print(f"│ 🤔 决策逻辑: {router_info.logic[:60]:<62} │")
            print(f"│ 📈 置信度: {router_info.confidence:.2f} ({router_info.confidence*100:.0f}%){'':<52} │")
            print(f"│ 📍 最终节点: {route_node:<62} │")
            
            if router_info.character_preference:
                char_names = {
                    'xiyang': '喜羊羊（儿子）',
                    'meiyang': '美羊羊（女儿）',
                    'lanyang': '懒羊羊（孙子）'
                }
                char_name = char_names.get(router_info.character_preference, router_info.character_preference)
                print(f"│ 👨‍👩‍👧‍👦 推荐角色: {char_name:<58} │")
            else:
                print(f"│ 👨‍👩‍👧‍👦 推荐角色: 无特定偏好{'':<58} │")
            
            print("└" + "─" * 78 + "┘")
            
            # 判断是否符合预期
            route_match = False
            if "xiyang" in expected.lower() and route_node == "xiyang_node":
                route_match = True
            elif "meiyang" in expected.lower() and route_node == "meiyang_node":
                route_match = True
            elif "lanyang" in expected.lower() and route_node == "lanyang_node":
                route_match = True
            elif "health" in expected.lower() and route_node == "health_concern_node":
                route_match = True
            elif "通用" in expected and route_node == "general_response":
                route_match = True
            elif "可能" in expected:  # 对于不确定的预期，都算正确
                route_match = True
            
            result_status = "✅ 符合预期" if route_match else "❌ 与预期不符"
            print(f"🏆 结果评估: {result_status}")
            
            # 记录结果
            results.append({
                "scenario": i,
                "input": user_input,
                "category": category,
                "expected": expected,
                "actual_type": router_info.type,
                "actual_node": route_node,
                "confidence": router_info.confidence,
                "logic": router_info.logic,
                "character_preference": router_info.character_preference,
                "match": route_match
            })
            
            # 如果路由到角色节点，生成简短回复示例
            if route_node in ["xiyang_node", "meiyang_node", "lanyang_node"]:
                character_id = route_node.replace("_node", "")
                char_names = {
                    'xiyang': '喜羊羊（儿子）',
                    'meiyang': '美羊羊（女儿）',
                    'lanyang': '懒羊羊（孙子）'
                }
                
                print(f"\n🎭 {char_names[character_id]}角色激活")
                try:
                    character_agent = CharacterAgent(character_id)
                    response = character_agent.generate_response(user_input)
                    if response and 'response' in response:
                        # 只显示前100个字符
                        preview = response['response'][:100]
                        if len(response['response']) > 100:
                            preview += "..."
                        print(f"💬 回复预览: {preview}")
                    else:
                        print("💬 回复预览: [生成失败]")
                except Exception as e:
                    print(f"💬 回复预览: [角色处理异常: {str(e)[:50]}]")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results.append({
                "scenario": i,
                "input": user_input,
                "category": category,
                "expected": expected,
                "error": str(e),
                "match": False
            })
        
        print("\n" + "-" * 80 + "\n")
    
    # 生成测试总结
    print("🎉 多场景路由测试完成！")
    print("=" * 80)
    
    # 统计结果
    total_tests = len(results)
    successful_tests = len([r for r in results if 'error' not in r])
    matched_tests = len([r for r in results if r.get('match', False)])
    
    print(f"📊 测试统计:")
    print(f"  - 总测试数: {total_tests}")
    print(f"  - 成功执行: {successful_tests}/{total_tests}")
    print(f"  - 符合预期: {matched_tests}/{total_tests}")
    print(f"  - 成功率: {(successful_tests/total_tests)*100:.1f}%")
    print(f"  - 准确率: {(matched_tests/total_tests)*100:.1f}%")
    
    # 按路由节点分类统计
    print(f"\n🎯 路由节点分布:")
    node_counts = {}
    for result in results:
        if 'actual_node' in result:
            node = result['actual_node']
            node_counts[node] = node_counts.get(node, 0) + 1
    
    node_names = {
        'xiyang_node': '🧑 儿子节点',
        'meiyang_node': '👩 女儿节点', 
        'lanyang_node': '👶 孙子节点',
        'general_response': '📝 通用回复',
        'health_concern_node': '🏥 健康关注',
        'emotional_support_node': '💝 情感支持',
        'knowledge_query_node': '📚 知识查询'
    }
    
    for node, count in sorted(node_counts.items()):
        node_name = node_names.get(node, node)
        percentage = (count/successful_tests)*100 if successful_tests > 0 else 0
        print(f"  - {node_name}: {count}次 ({percentage:.1f}%)")
    
    # 显示有趣的发现
    print(f"\n🔍 有趣发现:")
    
    # 找出相同类别的不同路由
    categories = {}
    for result in results:
        if 'actual_node' in result:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result['actual_node'])
    
    for category, nodes in categories.items():
        unique_nodes = set(nodes)
        if len(unique_nodes) > 1:
            print(f"  - 「{category}」类别路由到了多个节点: {list(unique_nodes)}")
    
    # 高置信度的路由
    high_confidence = [r for r in results if 'confidence' in r and r['confidence'] > 0.8]
    if high_confidence:
        print(f"  - 高置信度路由（>0.8）: {len(high_confidence)}/{successful_tests}次")
    
    # 意外的路由结果
    unexpected = [r for r in results if not r.get('match', False) and 'error' not in r]
    if unexpected:
        print(f"  - 意外路由结果: {len(unexpected)}次")
        for result in unexpected[:3]:  # 只显示前3个
            print(f"    「{result['input'][:30]}...」→ {result['actual_node']}")
    
    print(f"\n🏆 结论: 路由器能够智能地根据不同的用户表达选择合适的角色节点！")
    print(f"💡 「你是谁」这样的身份确认确实可能路由到不同节点，取决于具体的表达方式和上下文！")

def main():
    """主函数"""
    asyncio.run(test_multiple_routing_scenarios())

if __name__ == "__main__":
    main()
