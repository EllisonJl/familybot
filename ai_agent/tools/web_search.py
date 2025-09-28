"""
联网搜索工具 - 实时获取最新信息
"""

import requests
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re


class WebSearchTool:
    """联网搜索工具类"""
    
    def __init__(self):
        """初始化搜索工具"""
        self.api_url = "https://v1.search-api.ovh/api/search"
        self.api_key = "5b926162c800936f37c77a7208e6cc619bd4c07dfa3c1401b84b6059c9eba596"
        self.headers = {
            'API-KEY': self.api_key,
            'User-Agent': 'FamilyBot/1.0'
        }
        
    def should_search(self, query: str) -> bool:
        """
        判断是否需要进行联网搜索
        
        Args:
            query: 用户查询
            
        Returns:
            是否需要搜索
        """
        # 实时信息关键词
        real_time_keywords = [
            '今天', '现在', '最新', '当前', '实时', '最近',
            '新闻', '股价', '汇率', '天气', '疫情', '政策',
            '发布', '更新', '宣布', '公布', '报道', '消息',
            '今年', '2024', '2025', '本月', '这周', '昨天',
            '价格', '市场', '股市', '比特币', '房价', '油价'
        ]
        
        # 检查是否包含实时信息关键词
        query_lower = query.lower()
        for keyword in real_time_keywords:
            if keyword in query:
                return True
                
        # 检查问句模式
        question_patterns = [
            r'.*最新.*怎么样',
            r'.*现在.*价格',
            r'.*今天.*发生',
            r'.*最近.*消息',
            r'.*当前.*状况'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, query):
                return True
        
        return False
    
    async def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            搜索结果字典
        """
        try:
            print(f"🔍 开始联网搜索: {query}")
            
            # 构建请求参数
            params = {
                'q': query,
                'num': max_results,
                'hl': 'zh-CN',
                'gl': 'CN'
            }
            
            # 发送异步请求
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(
                    self.api_url, 
                    headers=self.headers, 
                    params=params,
                    timeout=10
                )
            )
            
            if response.status_code == 200:
                data = response.json()
                processed_results = self._process_search_results(data, query)
                print(f"✅ 搜索完成，找到 {len(processed_results.get('results', []))} 个结果")
                return processed_results
            else:
                print(f"❌ 搜索API请求失败: {response.status_code}")
                return self._create_error_result(f"搜索服务暂时不可用 (错误码: {response.status_code})")
                
        except asyncio.TimeoutError:
            print("❌ 搜索请求超时")
            return self._create_error_result("搜索请求超时，请稍后重试")
        except requests.RequestException as e:
            print(f"❌ 搜索请求异常: {e}")
            return self._create_error_result(f"网络连接错误: {str(e)}")
        except Exception as e:
            print(f"❌ 搜索处理异常: {e}")
            return self._create_error_result(f"搜索处理失败: {str(e)}")
    
    def _process_search_results(self, data: Dict, query: str) -> Dict[str, Any]:
        """
        处理搜索结果
        
        Args:
            data: 原始搜索数据
            query: 搜索查询
            
        Returns:
            处理后的结果
        """
        results = []
        
        # 提取搜索结果 - 支持多种API响应格式
        organic_results = []
        
        # 检查SerpAPI格式: data.data.organic_results
        if 'data' in data and isinstance(data['data'], dict) and 'organic_results' in data['data']:
            organic_results = data['data']['organic_results']
            print(f"🔍 使用SerpAPI格式，找到 {len(organic_results)} 个有机结果")
        # 检查直接格式: data.results  
        elif 'results' in data and isinstance(data['results'], list):
            organic_results = data['results']
            print(f"🔍 使用直接格式，找到 {len(organic_results)} 个结果")
        # 检查其他可能的格式
        elif 'organic_results' in data:
            organic_results = data['organic_results']
            print(f"🔍 使用有机结果格式，找到 {len(organic_results)} 个结果")
        
        # 处理搜索结果
        if organic_results and isinstance(organic_results, list):
            for item in organic_results[:5]:  # 限制前5个结果
                if isinstance(item, dict):
                    result = {
                        'title': item.get('title', '').strip(),
                        'url': item.get('link', item.get('url', '')).strip(),  # SerpAPI使用'link'
                        'snippet': item.get('snippet', '').strip(),
                        'source': self._extract_domain(item.get('link', item.get('url', '')))
                    }
                    
                    # 过滤有效结果
                    if result['title'] and result['snippet']:
                        results.append(result)
                        print(f"  ✅ 添加结果: {result['title'][:50]}...")
        
        # 构建总结
        summary = self._create_search_summary(results, query)
        
        # 获取总结果数（从不同可能的位置）
        total_count = len(results)
        if 'data' in data and isinstance(data['data'], dict):
            if 'search_information' in data['data'] and 'total_results' in data['data']['search_information']:
                total_count = data['data']['search_information']['total_results']
        elif 'total_results' in data:
            total_count = data['total_results']
        
        return {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'total_results': total_count,
            'results': results,
            'summary': summary,
            'status': 'success'
        }
    
    def _create_search_summary(self, results: List[Dict], query: str) -> str:
        """
        创建搜索结果总结
        
        Args:
            results: 搜索结果列表
            query: 搜索查询
            
        Returns:
            总结文本
        """
        if not results:
            return f"很抱歉，没有找到关于「{query}」的相关信息。"
        
        summary_parts = [f"🔍 关于「{query}」的最新信息：\n"]
        
        for i, result in enumerate(results[:3], 1):  # 使用前3个结果
            source = result['source']
            title = result['title'][:50] + "..." if len(result['title']) > 50 else result['title']
            snippet = result['snippet'][:100] + "..." if len(result['snippet']) > 100 else result['snippet']
            
            summary_parts.append(f"{i}. 【{source}】{title}")
            summary_parts.append(f"   {snippet}\n")
        
        # 添加搜索来源链接部分
        if results:
            summary_parts.append("\n📎 信息来源：")
            for i, result in enumerate(results[:3], 1):
                url = result['url']
                source = result['source']
                title = result['title'][:25] + "..." if len(result['title']) > 25 else result['title']
                summary_parts.append(f"{i}. {source} - {title} [链接{i}]({url})")
        
        summary_parts.append(f"\n📊 共找到 {len(results)} 条相关信息，数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(summary_parts)
    
    def _extract_domain(self, url: str) -> str:
        """
        从URL提取域名
        
        Args:
            url: 完整URL
            
        Returns:
            域名
        """
        try:
            if url.startswith(('http://', 'https://')):
                domain = url.split('/')[2]
                return domain.replace('www.', '')
            return url
        except:
            return "未知来源"
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        创建错误结果
        
        Args:
            error_message: 错误信息
            
        Returns:
            错误结果字典
        """
        return {
            'query': '',
            'timestamp': datetime.now().isoformat(),
            'total_results': 0,
            'results': [],
            'summary': error_message,
            'status': 'error'
        }


# 全局搜索工具实例
web_search_tool = WebSearchTool()


async def perform_web_search(query: str) -> Dict[str, Any]:
    """
    执行联网搜索的便捷函数
    
    Args:
        query: 搜索查询
        
    Returns:
        搜索结果
    """
    return await web_search_tool.search(query)


def should_use_web_search(query: str) -> bool:
    """
    判断是否应该使用联网搜索的便捷函数
    
    Args:
        query: 用户查询
        
    Returns:
        是否需要搜索
    """
    return web_search_tool.should_search(query)
