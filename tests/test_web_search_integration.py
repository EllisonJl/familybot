"""
联网搜索功能集成测试
测试自动触发和手动触发的联网搜索功能
"""

import asyncio
import sys
import os

# 添加AI Agent路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai_agent'))

from tools.web_search import web_search_tool, should_use_web_search, perform_web_search


async def test_search_trigger_detection():
    """测试搜索触发检测"""
    print("🧪 测试搜索触发检测...")
    
    # 应该触发搜索的查询
    should_search_queries = [
        "今天的股市怎么样",
        "最新新闻",
        "现在天气如何",
        "今年房价走势",
        "最近比特币价格"
    ]
    
    # 不应该触发搜索的查询
    should_not_search_queries = [
        "你好",
        "我爱你",
        "今天心情很好",
        "昨天我去了公园",
        "谢谢你的帮助"
    ]
    
    print("\n应该触发搜索的查询:")
    for query in should_search_queries:
        result = should_use_web_search(query)
        status = "✅" if result else "❌"
        print(f"  {status} '{query}' -> {result}")
    
    print("\n不应该触发搜索的查询:")
    for query in should_not_search_queries:
        result = should_use_web_search(query)
        status = "✅" if not result else "❌"
        print(f"  {status} '{query}' -> {result}")


async def test_web_search_api():
    """测试联网搜索API"""
    print("\n🧪 测试联网搜索API...")
    
    test_queries = [
        "Hello world",
        "Python programming",
        "最新科技新闻"
    ]
    
    for query in test_queries:
        print(f"\n🔍 搜索: '{query}'")
        try:
            result = await perform_web_search(query)
            if result:
                print(f"  ✅ 状态: {result.get('status', 'unknown')}")
                print(f"  📊 结果数量: {result.get('total_results', 0)}")
                print(f"  📝 总结: {result.get('summary', 'N/A')[:100]}...")
            else:
                print("  ❌ 搜索失败: 无返回结果")
        except Exception as e:
            print(f"  ❌ 搜索异常: {e}")


async def test_search_tool_initialization():
    """测试搜索工具初始化"""
    print("\n🧪 测试搜索工具初始化...")
    
    try:
        # 检查搜索工具属性
        print(f"  📡 API URL: {web_search_tool.api_url}")
        print(f"  🔑 API Key: {web_search_tool.api_key[:10]}...{web_search_tool.api_key[-10:]}")
        print(f"  🏷️ User-Agent: {web_search_tool.headers.get('User-Agent', 'N/A')}")
        print("  ✅ 搜索工具初始化正常")
    except Exception as e:
        print(f"  ❌ 搜索工具初始化失败: {e}")


async def main():
    """主测试函数"""
    print("🚀 联网搜索功能集成测试开始...\n")
    
    # 测试搜索工具初始化
    await test_search_tool_initialization()
    
    # 测试搜索触发检测
    await test_search_trigger_detection()
    
    # 测试联网搜索API
    await test_web_search_api()
    
    print("\n🎉 联网搜索功能集成测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
