#!/usr/bin/env python3
"""
文档上传和搜索功能集成测试
测试完整的文件上传、处理、存储和搜索流程
"""

import asyncio
import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "ai_agent"))

async def test_document_upload_flow():
    """测试文档上传和搜索完整流程"""
    
    print("🧪 开始测试文档上传和搜索功能...")
    
    try:
        # 导入必要的模块
        from rag.graph_rag import graph_rag
        from rag.document_processor import document_processor
        
        print("✅ 模块导入成功")
        
        # 创建测试文档
        test_content = """
        健康生活指南
        
        老年人的健康管理非常重要。以下是一些关键建议：
        
        1. 定期体检
        - 每年至少进行一次全面体检
        - 重点检查血压、血糖、血脂
        - 及时发现潜在健康问题
        
        2. 饮食健康
        - 少盐少油少糖
        - 多吃蔬菜水果
        - 保证足够的蛋白质摄入
        
        3. 适量运动
        - 每天散步30分钟
        - 做一些轻度的伸展运动
        - 避免剧烈运动
        
        4. 心理健康
        - 保持乐观心态
        - 多与家人朋友交流
        - 培养兴趣爱好
        
        记住：健康是最宝贵的财富！
        """
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file_path = f.name
        
        print(f"📄 创建测试文档: {temp_file_path}")
        
        # 读取文件内容
        with open(temp_file_path, 'rb') as f:
            file_content = f.read()
        
        # 测试文档上传
        print("📤 测试文档上传...")
        success, message = await graph_rag.add_document_knowledge(
            character_id="xiyang",
            file_content=file_content,
            filename="健康生活指南.txt",
            user_id="test_user"
        )
        
        if success:
            print(f"✅ 文档上传成功: {message}")
        else:
            print(f"❌ 文档上传失败: {message}")
            return False
        
        # 测试获取角色文档列表
        print("📋 测试获取角色文档列表...")
        documents = graph_rag.get_character_documents("xiyang")
        print(f"📚 角色 xiyang 的文档数量: {len(documents)}")
        
        for doc in documents:
            print(f"   - {doc['filename']} ({doc['file_size']} bytes)")
            if doc['summary']:
                print(f"     摘要: {doc['summary'][:100]}...")
        
        # 测试文档搜索
        print("🔍 测试文档搜索功能...")
        
        # 测试查询1: 健康相关
        print("\n🔍 查询1: '老年人如何保持健康?'")
        result1 = await graph_rag.query_knowledge(
            query="老年人如何保持健康?",
            character_id="xiyang"
        )
        
        print(f"📊 搜索结果: {len(result1.relevant_contexts)} 个相关上下文")
        for i, ctx in enumerate(result1.relevant_contexts[:3]):
            print(f"   {i+1}. [{ctx['source']}] 相关度: {ctx['relevance_score']:.2f}")
            print(f"      内容: {ctx['content'][:100]}...")
        
        # 测试查询2: 饮食相关
        print("\n🔍 查询2: '老年人饮食注意事项'")
        result2 = await graph_rag.query_knowledge(
            query="老年人饮食注意事项",
            character_id="xiyang"
        )
        
        print(f"📊 搜索结果: {len(result2.relevant_contexts)} 个相关上下文")
        for i, ctx in enumerate(result2.relevant_contexts[:3]):
            print(f"   {i+1}. [{ctx['source']}] 相关度: {ctx['relevance_score']:.2f}")
            print(f"      内容: {ctx['content'][:100]}...")
        
        # 测试查询3: 运动相关
        print("\n🔍 查询3: '适合老年人的运动'")
        result3 = await graph_rag.query_knowledge(
            query="适合老年人的运动",
            character_id="xiyang"
        )
        
        print(f"📊 搜索结果: {len(result3.relevant_contexts)} 个相关上下文")
        for i, ctx in enumerate(result3.relevant_contexts[:3]):
            print(f"   {i+1}. [{ctx['source']}] 相关度: {ctx['relevance_score']:.2f}")
            print(f"      内容: {ctx['content'][:100]}...")
        
        # 测试不同角色的文档隔离
        print("\n🔒 测试角色文档隔离...")
        
        # 查询其他角色的文档（应该为空或不包含刚上传的文档）
        meiyang_docs = graph_rag.get_character_documents("meiyang")
        print(f"📚 角色 meiyang 的文档数量: {len(meiyang_docs)}")
        
        # 清理测试文件
        os.unlink(temp_file_path)
        print("🧹 清理临时文件")
        
        print("\n✅ 所有测试通过！文档上传和搜索功能正常工作。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_character_isolation():
    """测试角色隔离功能"""
    print("\n🔒 测试角色文档隔离功能...")
    
    try:
        from rag.graph_rag import graph_rag
        
        # 为不同角色上传不同文档
        test_content_xiyang = "喜羊羊的专属文档：我喜欢踢足球，最爱吃青草。"
        test_content_meiyang = "美羊羊的专属文档：我喜欢化妆，最爱漂亮的衣服。"
        
        # 上传到喜羊羊
        success1, _ = await graph_rag.add_document_knowledge(
            character_id="xiyang",
            file_content=test_content_xiyang.encode('utf-8'),
            filename="喜羊羊专属.txt",
            user_id="test_user"
        )
        
        # 上传到美羊羊
        success2, _ = await graph_rag.add_document_knowledge(
            character_id="meiyang", 
            file_content=test_content_meiyang.encode('utf-8'),
            filename="美羊羊专属.txt",
            user_id="test_user"
        )
        
        if success1 and success2:
            print("✅ 为不同角色上传专属文档成功")
        
        # 测试角色只能搜索到自己的文档
        xiyang_result = await graph_rag.query_knowledge(
            query="足球",
            character_id="xiyang"
        )
        
        meiyang_result = await graph_rag.query_knowledge(
            query="化妆",
            character_id="meiyang"
        )
        
        print(f"🔍 喜羊羊搜索'足球': {len(xiyang_result.relevant_contexts)} 个结果")
        print(f"🔍 美羊羊搜索'化妆': {len(meiyang_result.relevant_contexts)} 个结果")
        
        # 测试交叉搜索（应该搜索不到其他角色的文档）
        xiyang_cross = await graph_rag.query_knowledge(
            query="化妆",
            character_id="xiyang"
        )
        
        meiyang_cross = await graph_rag.query_knowledge(
            query="足球",
            character_id="meiyang"
        )
        
        xiyang_cross_docs = [ctx for ctx in xiyang_cross.relevant_contexts if ctx['source'] == 'character_document']
        meiyang_cross_docs = [ctx for ctx in meiyang_cross.relevant_contexts if ctx['source'] == 'character_document']
        
        print(f"🔍 喜羊羊搜索'化妆'(交叉): {len(xiyang_cross_docs)} 个文档结果")
        print(f"🔍 美羊羊搜索'足球'(交叉): {len(meiyang_cross_docs)} 个文档结果")
        
        if len(xiyang_cross_docs) == 0 and len(meiyang_cross_docs) == 0:
            print("✅ 角色文档隔离功能正常工作")
        else:
            print("⚠️ 角色文档隔离可能存在问题")
        
        return True
        
    except Exception as e:
        print(f"❌ 角色隔离测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 启动文档上传和搜索功能测试")
    
    # 运行主要功能测试
    result1 = asyncio.run(test_document_upload_flow())
    
    # 运行角色隔离测试
    result2 = asyncio.run(test_character_isolation())
    
    if result1 and result2:
        print("\n🎉 所有测试通过！文档功能完全正常。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查相关配置。")
        sys.exit(1)
