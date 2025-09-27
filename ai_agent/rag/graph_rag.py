"""
Graph RAG 知识增强系统
基于图结构的知识检索和增强生成
集成文档搜索功能
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from openai import OpenAI

from config import Config
from models.state import GraphRAGResult
from rag.document_processor import document_processor


@dataclass
class KnowledgeNode:
    """知识节点"""
    id: str
    content: str
    node_type: str  # "concept", "fact", "advice", "story"
    domain: str     # "health", "family", "daily_life", "emotion"
    importance: float
    created_at: str
    metadata: Dict[str, Any]


@dataclass
class KnowledgeEdge:
    """知识边"""
    source_id: str
    target_id: str
    relation_type: str  # "relates_to", "caused_by", "helps_with", "example_of"
    weight: float
    metadata: Dict[str, Any]


class GraphRAGSystem:
    """Graph RAG 知识增强系统"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化Graph RAG系统"""
        if db_path is None:
            db_dir = Path(__file__).parent.parent / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "knowledge_graph.db")
        
        self.db_path = db_path
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.DASHSCOPE_BASE_URL
        )
        
        self._init_database()
        self._populate_initial_knowledge()
        
        print("✅ Graph RAG系统初始化完成")
    
    def _init_database(self):
        """初始化知识图数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 知识节点表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_nodes (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    created_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # 知识边表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (source_id) REFERENCES knowledge_nodes (id),
                    FOREIGN KEY (target_id) REFERENCES knowledge_nodes (id)
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nodes_domain 
                ON knowledge_nodes(domain)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nodes_type 
                ON knowledge_nodes(node_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_edges_source 
                ON knowledge_edges(source_id)
            """)
            
            conn.commit()
    
    def _populate_initial_knowledge(self):
        """填充初始知识库"""
        # 检查是否已有数据
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM knowledge_nodes")
            count = cursor.fetchone()[0]
            
            if count > 0:
                return  # 已有数据，跳过
        
        print("📚 正在初始化知识库...")
        
        # 初始知识节点
        initial_nodes = [
            # 健康知识
            KnowledgeNode(
                id="health_001",
                content="老年人应该每天至少散步30分钟，有助于改善心血管健康和骨骼强度",
                node_type="advice",
                domain="health",
                importance=0.9,
                created_at=datetime.now().isoformat(),
                metadata={"source": "医学建议", "audience": "老年人"}
            ),
            KnowledgeNode(
                id="health_002", 
                content="高血压患者应该定期监测血压，按时服药，少盐饮食",
                node_type="advice",
                domain="health",
                importance=0.95,
                created_at=datetime.now().isoformat(),
                metadata={"source": "医学指南", "condition": "高血压"}
            ),
            KnowledgeNode(
                id="health_003",
                content="充足的睡眠对老年人很重要，建议每晚7-8小时，保持规律作息",
                node_type="advice", 
                domain="health",
                importance=0.8,
                created_at=datetime.now().isoformat(),
                metadata={"source": "健康指南", "topic": "睡眠"}
            ),
            
            # 情感支持知识
            KnowledgeNode(
                id="emotion_001",
                content="当老人感到孤独时，可以通过聊天、回忆美好时光、听音乐来改善心情",
                node_type="advice",
                domain="emotion",
                importance=0.85,
                created_at=datetime.now().isoformat(),
                metadata={"emotion": "loneliness", "strategies": ["chat", "music", "memories"]}
            ),
            KnowledgeNode(
                id="emotion_002",
                content="家人的陪伴和关爱是老人心理健康的重要支撑",
                node_type="fact",
                domain="emotion",
                importance=0.9,
                created_at=datetime.now().isoformat(),
                metadata={"importance": "family_support"}
            ),
            
            # 家庭关系知识
            KnowledgeNode(
                id="family_001",
                content="定期与家人联系，分享日常生活，有助于维系亲情纽带",
                node_type="advice",
                domain="family",
                importance=0.8,
                created_at=datetime.now().isoformat(),
                metadata={"activity": "communication"}
            ),
            KnowledgeNode(
                id="family_002",
                content="孙辈的陪伴能给老人带来特别的快乐和生活动力",
                node_type="fact",
                domain="family",
                importance=0.85,
                created_at=datetime.now().isoformat(),
                metadata={"relationship": "grandparent-grandchild"}
            ),
            
            # 日常生活知识
            KnowledgeNode(
                id="daily_001",
                content="保持规律的作息时间，有助于身体健康和情绪稳定",
                node_type="advice",
                domain="daily_life",
                importance=0.75,
                created_at=datetime.now().isoformat(),
                metadata={"aspect": "routine"}
            ),
            KnowledgeNode(
                id="daily_002",
                content="适当的社交活动，如与邻居聊天、参加社区活动，有益身心健康",
                node_type="advice",
                domain="daily_life", 
                importance=0.8,
                created_at=datetime.now().isoformat(),
                metadata={"activity": "social"}
            )
        ]
        
        # 初始知识边
        initial_edges = [
            # 健康相关连接
            KnowledgeEdge("health_001", "health_003", "relates_to", 0.8, {"reason": "运动和睡眠都是健康要素"}),
            KnowledgeEdge("health_002", "health_001", "relates_to", 0.7, {"reason": "血压控制需要运动配合"}),
            
            # 情感和家庭连接
            KnowledgeEdge("emotion_001", "family_001", "helps_with", 0.9, {"reason": "家人联系缓解孤独"}),
            KnowledgeEdge("emotion_002", "family_002", "example_of", 0.85, {"reason": "孙辈陪伴是家人支撑的例子"}),
            
            # 日常生活连接
            KnowledgeEdge("daily_001", "health_003", "relates_to", 0.9, {"reason": "规律作息包含规律睡眠"}),
            KnowledgeEdge("daily_002", "emotion_001", "helps_with", 0.8, {"reason": "社交活动缓解孤独感"})
        ]
        
        # 批量插入数据
        self._batch_insert_nodes(initial_nodes)
        self._batch_insert_edges(initial_edges)
        
        print(f"✅ 已初始化 {len(initial_nodes)} 个知识节点和 {len(initial_edges)} 个知识边")
    
    def _batch_insert_nodes(self, nodes: List[KnowledgeNode]):
        """批量插入知识节点"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            node_data = [
                (
                    node.id, node.content, node.node_type, node.domain,
                    node.importance, node.created_at, json.dumps(node.metadata)
                )
                for node in nodes
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO knowledge_nodes 
                (id, content, node_type, domain, importance, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, node_data)
            
            conn.commit()
    
    def _batch_insert_edges(self, edges: List[KnowledgeEdge]):
        """批量插入知识边"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            edge_data = [
                (
                    edge.source_id, edge.target_id, edge.relation_type,
                    edge.weight, json.dumps(edge.metadata)
                )
                for edge in edges
            ]
            
            cursor.executemany("""
                INSERT INTO knowledge_edges 
                (source_id, target_id, relation_type, weight, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, edge_data)
            
            conn.commit()
    
    async def query_knowledge(
        self, 
        query: str, 
        character_id: Optional[str] = None,
        domain: Optional[str] = None, 
        limit: int = 5
    ) -> dict:
        """
        查询知识图谱和角色文档
        
        Args:
            query: 查询文本
            character_id: 角色ID，用于搜索角色专属文档
            domain: 知识域限制
            limit: 返回结果数量限制
            
        Returns:
            知识检索结果
        """
        try:
            print(f"🔍 Graph RAG 查询: {query[:50]}...")
            if character_id:
                print(f"🎭 角色: {character_id}")
            
            # 1. 查询扩展 - 生成相关关键词
            expanded_query = await self._expand_query(query)
            
            # 2. 检索相关节点（基础知识图谱）
            relevant_nodes = self._search_nodes(expanded_query, domain, limit)
            
            # 3. 搜索角色文档（如果提供了角色ID）
            document_results = []
            if character_id:
                document_results = await document_processor.search_in_character_documents(
                    character_id, query, limit
                )
                print(f"📄 在角色文档中找到 {len(document_results)} 个相关片段")
            
            # 4. 图遍历 - 查找相关联的节点
            connected_nodes = self._find_connected_nodes(relevant_nodes, limit // 2)
            
            # 5. 结果排序和过滤
            final_results = self._rank_and_filter_results(
                relevant_nodes + connected_nodes, query, limit // 2
            )
            
            # 6. 构建结果
            contexts = []
            sources = []
            
            # 添加知识图谱结果
            for node, score in final_results:
                contexts.append({
                    "content": node.content,
                    "domain": node.domain,
                    "type": node.node_type,
                    "relevance_score": score,
                    "metadata": node.metadata,
                    "source": "knowledge_graph"
                })
                sources.append(f"{node.domain}_{node.node_type}")
            
            # 添加文档搜索结果
            for doc_result in document_results:
                contexts.append({
                    "content": doc_result["content"],
                    "domain": "document",
                    "type": "document_chunk",
                    "relevance_score": doc_result["relevance_score"],
                    "metadata": {
                        "filename": doc_result["filename"],
                        "page_number": doc_result["page_number"],
                        "file_id": doc_result["file_id"]
                    },
                    "source": "character_document"
                })
                sources.append(f"document_{doc_result['filename']}")
            
            # 按相关性排序
            contexts.sort(key=lambda x: x["relevance_score"], reverse=True)
            contexts = contexts[:limit]  # 限制最终结果数量
            
            result = GraphRAGResult(
                relevant_contexts=contexts,
                knowledge_sources=list(set(sources)),
                confidence=max([ctx["relevance_score"] for ctx in contexts]) if contexts else 0.0,
                query_expansion=expanded_query
            )
            
            print(f"✅ Graph RAG 检索完成，找到 {len(contexts)} 个相关上下文")
            print(f"   - 知识图谱: {len([c for c in contexts if c['source'] == 'knowledge_graph'])} 个")
            print(f"   - 角色文档: {len([c for c in contexts if c['source'] == 'character_document'])} 个")
            
            return result
            
        except Exception as e:
            print(f"❌ Graph RAG 查询失败: {e}")
            return GraphRAGResult(
                relevant_contexts=[],
                knowledge_sources=[],
                confidence=0.0,
                query_expansion=[query]
            )
    
    async def _expand_query(self, query: str) -> List[str]:
        """查询扩展 - 生成相关关键词"""
        try:
            expansion_prompt = f"""
请为以下查询生成相关的关键词和同义词，帮助更好地检索知识：

查询: {query}

请生成5-10个相关关键词，包括：
1. 核心概念的同义词
2. 相关的主题词
3. 可能的搜索变体

只返回关键词列表，每行一个：
"""
            
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": expansion_prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            expanded_terms = response.choices[0].message.content.strip().split('\n')
            expanded_terms = [term.strip('- ').strip() for term in expanded_terms if term.strip()]
            
            # 添加原始查询
            return [query] + expanded_terms[:8]
            
        except Exception as e:
            print(f"⚠️ 查询扩展失败: {e}")
            return [query]
    
    def _search_nodes(self, query_terms: List[str], domain: Optional[str], limit: int) -> List[Tuple[KnowledgeNode, float]]:
        """搜索相关知识节点"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建搜索条件
                search_conditions = []
                params = []
                
                # 文本匹配条件
                for term in query_terms[:3]:  # 只使用前3个最重要的词
                    search_conditions.append("content LIKE ?")
                    params.append(f"%{term}%")
                
                # 域限制
                domain_condition = ""
                if domain:
                    domain_condition = "AND domain = ?"
                    params.append(domain)
                
                # 构建查询
                where_clause = " OR ".join(search_conditions)
                if not where_clause:
                    where_clause = "1=1"
                
                query_sql = f"""
                    SELECT id, content, node_type, domain, importance, created_at, metadata
                    FROM knowledge_nodes 
                    WHERE ({where_clause}) {domain_condition}
                    ORDER BY importance DESC, created_at DESC
                    LIMIT ?
                """
                params.append(limit)
                
                cursor.execute(query_sql, params)
                rows = cursor.fetchall()
                
                # 转换为KnowledgeNode对象并计算相关性分数
                results = []
                for row in rows:
                    node = KnowledgeNode(
                        id=row[0],
                        content=row[1],
                        node_type=row[2],
                        domain=row[3],
                        importance=row[4],
                        created_at=row[5],
                        metadata=json.loads(row[6])
                    )
                    
                    # 计算相关性分数（简化版本）
                    score = self._calculate_relevance_score(node, query_terms)
                    results.append((node, score))
                
                # 按分数排序
                results.sort(key=lambda x: x[1], reverse=True)
                return results
                
        except Exception as e:
            print(f"❌ 节点搜索失败: {e}")
            return []
    
    def _find_connected_nodes(self, nodes: List[Tuple[KnowledgeNode, float]], limit: int) -> List[Tuple[KnowledgeNode, float]]:
        """查找相关联的节点"""
        if not nodes:
            return []
        
        try:
            node_ids = [node.id for node, _ in nodes[:3]]  # 只使用前3个最相关的节点
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 查找相关联的节点
                placeholders = ",".join(["?"] * len(node_ids))
                query_sql = f"""
                    SELECT DISTINCT n.id, n.content, n.node_type, n.domain, 
                           n.importance, n.created_at, n.metadata, e.weight
                    FROM knowledge_nodes n
                    JOIN knowledge_edges e ON (n.id = e.target_id OR n.id = e.source_id)
                    WHERE (e.source_id IN ({placeholders}) OR e.target_id IN ({placeholders}))
                    AND n.id NOT IN ({placeholders})
                    ORDER BY e.weight DESC, n.importance DESC
                    LIMIT ?
                """
                
                params = node_ids + node_ids + node_ids + [limit]
                cursor.execute(query_sql, params)
                rows = cursor.fetchall()
                
                # 转换结果
                connected_results = []
                for row in rows:
                    node = KnowledgeNode(
                        id=row[0],
                        content=row[1],
                        node_type=row[2],
                        domain=row[3],
                        importance=row[4],
                        created_at=row[5],
                        metadata=json.loads(row[6])
                    )
                    
                    # 连接节点的分数基于边权重和重要性
                    edge_weight = row[7]
                    score = (edge_weight * 0.6 + node.importance * 0.4)
                    connected_results.append((node, score))
                
                return connected_results
                
        except Exception as e:
            print(f"❌ 连接节点查找失败: {e}")
            return []
    
    def _calculate_relevance_score(self, node: KnowledgeNode, query_terms: List[str]) -> float:
        """计算节点与查询的相关性分数"""
        content_lower = node.content.lower()
        
        # 文本匹配分数
        match_score = 0.0
        for term in query_terms:
            if term.lower() in content_lower:
                match_score += 1.0
        
        # 标准化匹配分数
        match_score = match_score / len(query_terms) if query_terms else 0.0
        
        # 综合分数：匹配度 + 重要性
        final_score = match_score * 0.7 + node.importance * 0.3
        
        return min(final_score, 1.0)
    
    def _rank_and_filter_results(
        self, 
        results: List[Tuple[KnowledgeNode, float]], 
        original_query: str, 
        limit: int
    ) -> List[Tuple[KnowledgeNode, float]]:
        """排序和过滤最终结果"""
        # 去重（基于节点ID）
        seen_ids = set()
        unique_results = []
        
        for node, score in results:
            if node.id not in seen_ids:
                seen_ids.add(node.id)
                unique_results.append((node, score))
        
        # 按分数排序
        unique_results.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N个结果
        return unique_results[:limit]
    
    def add_knowledge_node(self, node: KnowledgeNode) -> bool:
        """添加新的知识节点"""
        try:
            self._batch_insert_nodes([node])
            print(f"✅ 已添加知识节点: {node.id}")
            return True
        except Exception as e:
            print(f"❌ 添加知识节点失败: {e}")
            return False
    
    def add_knowledge_edge(self, edge: KnowledgeEdge) -> bool:
        """添加新的知识边"""
        try:
            self._batch_insert_edges([edge])
            print(f"✅ 已添加知识边: {edge.source_id} -> {edge.target_id}")
            return True
        except Exception as e:
            print(f"❌ 添加知识边失败: {e}")
            return False
    
    async def add_document_knowledge(
        self, 
        character_id: str, 
        file_content: bytes, 
        filename: str, 
        user_id: str
    ) -> Tuple[bool, str]:
        """
        添加文档知识到角色知识库
        
        Args:
            character_id: 角色ID
            file_content: 文件内容
            filename: 文件名
            user_id: 用户ID
            
        Returns:
            (成功标志, 消息)
        """
        try:
            print(f"📚 为角色 {character_id} 添加文档知识: {filename}")
            
            success, message, metadata = await document_processor.upload_file(
                file_content, filename, character_id, user_id
            )
            
            if success:
                print(f"✅ 文档知识添加成功: {filename}")
                return True, f"文档 {filename} 上传成功，已添加到 {character_id} 的知识库"
            else:
                print(f"❌ 文档知识添加失败: {message}")
                return False, message
                
        except Exception as e:
            print(f"❌ 添加文档知识失败: {e}")
            return False, f"文档处理失败: {str(e)}"
    
    def get_character_documents(self, character_id: str) -> List[Dict[str, Any]]:
        """
        获取角色的所有文档
        
        Args:
            character_id: 角色ID
            
        Returns:
            文档列表
        """
        try:
            files = document_processor.get_character_files(character_id)
            
            return [
                {
                    "file_id": file.file_id,
                    "filename": file.filename,
                    "file_type": file.file_type,
                    "file_size": file.file_size,
                    "upload_time": file.upload_time,
                    "page_count": file.page_count,
                    "word_count": file.word_count,
                    "summary": file.summary,
                    "keywords": file.keywords
                }
                for file in files
            ]
            
        except Exception as e:
            print(f"❌ 获取角色文档失败: {e}")
            return []
    
    def delete_character_document(self, character_id: str, file_id: str) -> bool:
        """
        删除角色文档
        
        Args:
            character_id: 角色ID
            file_id: 文件ID
            
        Returns:
            删除是否成功
        """
        try:
            return document_processor.delete_character_file(character_id, file_id)
        except Exception as e:
            print(f"❌ 删除角色文档失败: {e}")
            return False


# 创建全局Graph RAG实例
graph_rag = GraphRAGSystem()
