"""
文档处理器
支持PDF、Word、TXT等格式文档的解析和知识提取
"""

import os
import json
import hashlib
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import uuid

# 文档解析库
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from openai import OpenAI
from config import Config


@dataclass
class DocumentMetadata:
    """文档元数据"""
    file_id: str
    filename: str
    file_path: str
    file_size: int
    file_type: str
    upload_time: str
    character_id: str
    user_id: str
    content_hash: str
    page_count: int = 0
    word_count: int = 0
    summary: str = ""
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class DocumentChunk:
    """文档片段"""
    chunk_id: str
    file_id: str
    content: str
    chunk_index: int
    page_number: int = 0
    chunk_type: str = "text"  # text, table, image
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self, db_path: Optional[str] = None, storage_path: Optional[str] = None):
        """初始化文档处理器"""
        if db_path is None:
            db_dir = Path(__file__).parent.parent / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "document_storage.db")
            
        if storage_path is None:
            storage_path = str(Path(__file__).parent.parent / "data" / "uploaded_files")
            
        self.db_path = db_path
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.client = OpenAI(
            api_key=Config.DASHSCOPE_API_KEY,
            base_url=Config.DASHSCOPE_BASE_URL
        )
        
        self._init_database()
        print("✅ 文档处理器初始化完成")
    
    def _init_database(self):
        """初始化文档存储数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 文档元数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_metadata (
                    file_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type TEXT NOT NULL,
                    upload_time TEXT NOT NULL,
                    character_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    page_count INTEGER DEFAULT 0,
                    word_count INTEGER DEFAULT 0,
                    summary TEXT DEFAULT '',
                    keywords TEXT DEFAULT '[]'
                )
            """)
            
            # 文档片段表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    file_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    page_number INTEGER DEFAULT 0,
                    chunk_type TEXT DEFAULT 'text',
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (file_id) REFERENCES document_metadata (file_id)
                )
            """)
            
            # 角色文件关联表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    file_id TEXT NOT NULL,
                    access_time TEXT NOT NULL,
                    FOREIGN KEY (file_id) REFERENCES document_metadata (file_id),
                    UNIQUE(character_id, file_id)
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metadata_character 
                ON document_metadata(character_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_file 
                ON document_chunks(file_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_character_files_character 
                ON character_files(character_id)
            """)
            
            conn.commit()
    
    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        character_id: str, 
        user_id: str
    ) -> Tuple[bool, str, Optional[DocumentMetadata]]:
        """
        上传文件并处理
        
        Args:
            file_content: 文件内容
            filename: 文件名
            character_id: 角色ID
            user_id: 用户ID
            
        Returns:
            (成功标志, 消息, 文档元数据)
        """
        try:
            print(f"📤 开始处理文件上传: {filename}")
            
            # 检查文件类型
            file_type = self._get_file_type(filename)
            if not self._is_supported_file_type(file_type):
                return False, f"不支持的文件类型: {file_type}", None
            
            # 生成文件ID和路径
            file_id = str(uuid.uuid4())
            content_hash = hashlib.md5(file_content).hexdigest()
            
            # 检查是否已上传过相同文件
            existing_file = self._check_duplicate_file(content_hash, character_id)
            if existing_file:
                return False, "该角色已上传过相同内容的文件", existing_file
            
            # 保存文件
            file_path = self._save_file(file_content, file_id, filename)
            
            # 解析文档内容
            chunks = await self._parse_document(file_path, file_id, file_type)
            print(f"📖 文档解析结果: 找到 {len(chunks)} 个文本块")
            if not chunks:
                return False, f"文档解析失败：文件 {filename} 没有提取到有效文本内容，可能是空文件、加密文件或格式错误", None
            
            # 生成文档摘要和关键词
            summary, keywords = await self._generate_document_summary(chunks)
            
            # 创建文档元数据
            metadata = DocumentMetadata(
                file_id=file_id,
                filename=filename,
                file_path=file_path,
                file_size=len(file_content),
                file_type=file_type,
                upload_time=datetime.now().isoformat(),
                character_id=character_id,
                user_id=user_id,
                content_hash=content_hash,
                page_count=max([chunk.page_number for chunk in chunks]) if chunks else 0,
                word_count=sum([len(chunk.content) for chunk in chunks]),
                summary=summary,
                keywords=keywords
            )
            
            # 存储到数据库
            self._store_document_metadata(metadata)
            self._store_document_chunks(chunks)
            self._add_character_file_relation(character_id, file_id)
            
            print(f"✅ 文件上传处理完成: {filename}, ID: {file_id}")
            return True, "文件上传和处理成功", metadata
            
        except Exception as e:
            print(f"❌ 文件上传处理失败: {e}")
            return False, f"文件处理失败: {str(e)}", None
    
    def _get_file_type(self, filename: str) -> str:
        """获取文件类型"""
        return Path(filename).suffix.lower()
    
    def _is_supported_file_type(self, file_type: str) -> bool:
        """检查是否支持的文件类型"""
        supported_types = ['.txt', '.md']
        
        if PDF_AVAILABLE:
            supported_types.extend(['.pdf'])
            
        if DOCX_AVAILABLE:
            supported_types.extend(['.docx', '.doc'])
            
        return file_type in supported_types
    
    def _check_duplicate_file(self, content_hash: str, character_id: str) -> Optional[DocumentMetadata]:
        """检查重复文件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM document_metadata 
                    WHERE content_hash = ? AND character_id = ?
                """, (content_hash, character_id))
                
                row = cursor.fetchone()
                if row:
                    return DocumentMetadata(
                        file_id=row[0],
                        filename=row[1],
                        file_path=row[2],
                        file_size=row[3],
                        file_type=row[4],
                        upload_time=row[5],
                        character_id=row[6],
                        user_id=row[7],
                        content_hash=row[8],
                        page_count=row[9],
                        word_count=row[10],
                        summary=row[11],
                        keywords=json.loads(row[12])
                    )
                return None
        except Exception as e:
            print(f"❌ 检查重复文件失败: {e}")
            return None
    
    def _save_file(self, file_content: bytes, file_id: str, filename: str) -> str:
        """保存文件到本地存储"""
        file_extension = Path(filename).suffix
        safe_filename = f"{file_id}{file_extension}"
        file_path = self.storage_path / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
            
        return str(file_path)
    
    async def _parse_document(self, file_path: str, file_id: str, file_type: str) -> List[DocumentChunk]:
        """解析文档内容"""
        try:
            if file_type == '.txt' or file_type == '.md':
                return self._parse_text_file(file_path, file_id)
            elif file_type == '.pdf' and PDF_AVAILABLE:
                return self._parse_pdf_file(file_path, file_id)
            elif file_type in ['.docx', '.doc'] and DOCX_AVAILABLE:
                return self._parse_docx_file(file_path, file_id)
            else:
                print(f"⚠️ 不支持的文件类型: {file_type}")
                return []
                
        except Exception as e:
            print(f"❌ 文档解析失败: {e}")
            return []
    
    def _parse_text_file(self, file_path: str, file_id: str) -> List[DocumentChunk]:
        """解析文本文件"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按段落分割
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > 20:  # 降低最小长度要求
                    chunk = DocumentChunk(
                        chunk_id=f"{file_id}_chunk_{i}",
                        file_id=file_id,
                        content=paragraph,
                        chunk_index=i,
                        page_number=1,
                        chunk_type="text"
                    )
                    chunks.append(chunk)
                    
            return chunks
            
        except Exception as e:
            print(f"❌ 文本文件解析失败: {e}")
            return []
    
    def _parse_pdf_file(self, file_path: str, file_id: str) -> List[DocumentChunk]:
        """解析PDF文件"""
        chunks = []
        
        try:
            print(f"📖 开始解析PDF文件: {file_path}")
            with pdfplumber.open(file_path) as pdf:
                print(f"📄 PDF页数: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    print(f"📄 第{page_num}页提取的文本长度: {len(text) if text else 0}")
                    
                    if text and text.strip():
                        # 按段落分割
                        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                        print(f"📄 第{page_num}页分割出 {len(paragraphs)} 个段落")
                        
                        for i, paragraph in enumerate(paragraphs):
                            # 降低最小长度要求到20个字符
                            if len(paragraph) > 20:
                                chunk = DocumentChunk(
                                    chunk_id=f"{file_id}_page_{page_num}_chunk_{i}",
                                    file_id=file_id,
                                    content=paragraph,
                                    chunk_index=len(chunks),
                                    page_number=page_num,
                                    chunk_type="text"
                                )
                                chunks.append(chunk)
                                print(f"✅ 添加文本块 {len(chunks)}: {paragraph[:50]}...")
                                
            print(f"📖 PDF解析完成，共提取 {len(chunks)} 个文本块")
            return chunks
            
        except Exception as e:
            print(f"❌ PDF文件解析失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_docx_file(self, file_path: str, file_id: str) -> List[DocumentChunk]:
        """解析Word文档"""
        chunks = []
        
        try:
            doc = DocxDocument(file_path)
            
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if text and len(text) > 20:  # 降低最小长度要求
                    chunk = DocumentChunk(
                        chunk_id=f"{file_id}_para_{i}",
                        file_id=file_id,
                        content=text,
                        chunk_index=i,
                        page_number=1,  # Word文档没有明确的页面概念
                        chunk_type="text"
                    )
                    chunks.append(chunk)
                    
            return chunks
            
        except Exception as e:
            print(f"❌ Word文档解析失败: {e}")
            return []
    
    async def _generate_document_summary(self, chunks: List[DocumentChunk]) -> Tuple[str, List[str]]:
        """生成文档摘要和关键词"""
        try:
            # 取前几个chunk作为样本
            sample_content = "\n\n".join([chunk.content for chunk in chunks[:5]])
            
            summary_prompt = f"""
请为以下文档内容生成一个简洁的摘要（不超过200字）：

{sample_content[:1000]}

摘要应该包含：
1. 文档的主要主题
2. 关键信息点
3. 文档类型（如：医学报告、技术文档、个人记录等）

只返回摘要内容：
"""
            
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            
            # 生成关键词
            keywords_prompt = f"""
基于以下文档内容，提取5-10个关键词：

{sample_content[:1000]}

只返回关键词列表，每行一个：
"""
            
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": keywords_prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            keywords_text = response.choices[0].message.content.strip()
            keywords = [kw.strip('- ').strip() for kw in keywords_text.split('\n') if kw.strip()]
            
            return summary, keywords[:10]
            
        except Exception as e:
            print(f"❌ 生成文档摘要失败: {e}")
            return "文档摘要生成失败", []
    
    def _store_document_metadata(self, metadata: DocumentMetadata):
        """存储文档元数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO document_metadata 
                (file_id, filename, file_path, file_size, file_type, upload_time, 
                 character_id, user_id, content_hash, page_count, word_count, summary, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.file_id, metadata.filename, metadata.file_path,
                metadata.file_size, metadata.file_type, metadata.upload_time,
                metadata.character_id, metadata.user_id, metadata.content_hash,
                metadata.page_count, metadata.word_count, metadata.summary,
                json.dumps(metadata.keywords)
            ))
            conn.commit()
    
    def _store_document_chunks(self, chunks: List[DocumentChunk]):
        """存储文档片段"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            chunk_data = [
                (
                    chunk.chunk_id, chunk.file_id, chunk.content,
                    chunk.chunk_index, chunk.page_number, chunk.chunk_type,
                    json.dumps(chunk.metadata)
                )
                for chunk in chunks
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO document_chunks 
                (chunk_id, file_id, content, chunk_index, page_number, chunk_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, chunk_data)
            
            conn.commit()
    
    def _add_character_file_relation(self, character_id: str, file_id: str):
        """添加角色文件关联"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO character_files 
                (character_id, file_id, access_time)
                VALUES (?, ?, ?)
            """, (character_id, file_id, datetime.now().isoformat()))
            conn.commit()
    
    def get_character_files(self, character_id: str) -> List[DocumentMetadata]:
        """获取角色的所有文件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT dm.* FROM document_metadata dm
                    JOIN character_files cf ON dm.file_id = cf.file_id
                    WHERE cf.character_id = ?
                    ORDER BY dm.upload_time DESC
                """, (character_id,))
                
                rows = cursor.fetchall()
                files = []
                
                for row in rows:
                    files.append(DocumentMetadata(
                        file_id=row[0],
                        filename=row[1],
                        file_path=row[2],
                        file_size=row[3],
                        file_type=row[4],
                        upload_time=row[5],
                        character_id=row[6],
                        user_id=row[7],
                        content_hash=row[8],
                        page_count=row[9],
                        word_count=row[10],
                        summary=row[11],
                        keywords=json.loads(row[12])
                    ))
                
                return files
                
        except Exception as e:
            print(f"❌ 获取角色文件失败: {e}")
            return []
    
    async def search_in_character_documents(
        self, 
        character_id: str, 
        query: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """在角色的文档中搜索相关内容"""
        try:
            print(f"🔍 搜索文档 - 角色: {character_id}, 查询: '{query}', 限制: {limit}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 先检查是否有该角色的文档
                cursor.execute("""
                    SELECT COUNT(*) FROM character_files WHERE character_id = ?
                """, (character_id,))
                file_count = cursor.fetchone()[0]
                print(f"📚 角色 {character_id} 拥有 {file_count} 个文档")
                
                # 智能提取关键词进行搜索
                import re
                
                # 手动分割中文短语和词组
                common_patterns = [
                    r'爆米花镇',
                    r'大骚动', 
                    r'嘎嘟',
                    r'玉米精灵',
                    r'火种石',
                    r'皮皮猴',
                    r'胖墩狗'
                ]
                
                # 查找已知的重要词组
                search_terms = []
                for pattern in common_patterns:
                    if re.search(pattern, query):
                        search_terms.append(pattern)
                
                # 如果没有找到特定词组，使用基本的词汇分割
                if not search_terms:
                    # 提取2-6个字符的中文词组
                    words = []
                    for i in range(len(query)):
                        for j in range(i+2, min(i+7, len(query)+1)):
                            word = query[i:j]
                            if re.match(r'^[\u4e00-\u9fff]+$', word):
                                words.append(word)
                    
                    # 过滤停用词和短词
                    stop_words = {'是', '的', '了', '在', '和', '与', '或', '这个', '那个', '什么', '内容', '说了', '故事', '这是', '那是'}
                    search_terms = [word for word in words if word not in stop_words and len(word) >= 2]
                    
                    # 去重并保持顺序
                    seen = set()
                    search_terms = [word for word in search_terms if not (word in seen or seen.add(word))]
                
                # 如果还是没有找到，使用原始查询
                if not search_terms:
                    search_terms = [query]
                
                print(f"🔍 提取的关键词: {search_terms[:5]}")  # 限制显示前5个
                
                all_results = []
                
                # 对每个查询词进行搜索
                for term in search_terms:
                    cursor.execute("""
                        SELECT dc.content, dc.page_number, dm.filename, dm.file_id
                        FROM document_chunks dc
                        JOIN document_metadata dm ON dc.file_id = dm.file_id
                        JOIN character_files cf ON dm.file_id = cf.file_id
                        WHERE cf.character_id = ? AND dc.content LIKE ?
                        ORDER BY dm.upload_time DESC
                        LIMIT ?
                    """, (character_id, f"%{term}%", limit))
                    
                    rows = cursor.fetchall()
                    print(f"🔍 词汇 '{term}' 找到 {len(rows)} 个结果")
                    
                    for row in rows:
                        result = {
                            "content": row[0],
                            "page_number": row[1],
                            "filename": row[2],
                            "file_id": row[3],
                            "relevance_score": 0.8  # 简化的相关性分数
                        }
                        # 避免重复结果
                        if not any(r["content"] == result["content"] for r in all_results):
                            all_results.append(result)
                
                print(f"📄 总共找到 {len(all_results)} 个唯一结果")
                return all_results[:limit]
                
        except Exception as e:
            print(f"❌ 文档搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_character_file(self, character_id: str, file_id: str) -> bool:
        """删除角色的文件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查文件是否属于该角色
                cursor.execute("""
                    SELECT file_path FROM document_metadata 
                    WHERE file_id = ? AND character_id = ?
                """, (file_id, character_id))
                
                row = cursor.fetchone()
                if not row:
                    return False
                
                file_path = row[0]
                
                # 删除数据库记录
                cursor.execute("DELETE FROM character_files WHERE character_id = ? AND file_id = ?", 
                             (character_id, file_id))
                cursor.execute("DELETE FROM document_chunks WHERE file_id = ?", (file_id,))
                cursor.execute("DELETE FROM document_metadata WHERE file_id = ?", (file_id,))
                
                # 删除物理文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                conn.commit()
                print(f"✅ 已删除文件: {file_id}")
                return True
                
        except Exception as e:
            print(f"❌ 删除文件失败: {e}")
            return False


# 创建全局文档处理器实例
document_processor = DocumentProcessor()
