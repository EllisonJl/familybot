#!/usr/bin/env python3
"""
PDF文件上传测试
"""

import asyncio
import requests
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    """创建一个简单的测试PDF文件"""
    buffer = io.BytesIO()
    
    # 创建PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # 添加文本内容
    p.drawString(100, height - 100, "测试PDF文档")
    p.drawString(100, height - 150, "这是一个测试用的PDF文件。")
    p.drawString(100, height - 200, "我们正在测试文档上传功能。")
    p.drawString(100, height - 250, "老年人健康管理是非常重要的话题。")
    p.drawString(100, height - 300, "建议定期体检，保持良好的饮食习惯。")
    p.drawString(100, height - 350, "适量运动可以增强体质，改善心情。")
    p.drawString(100, height - 400, "保持积极乐观的心态对健康很有益处。")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()

async def test_pdf_upload():
    """测试PDF文件上传API"""
    try:
        print("📄 创建测试PDF文件...")
        pdf_content = create_test_pdf()
        print(f"✅ PDF文件创建完成，大小: {len(pdf_content)} bytes")
        
        print("📤 准备上传PDF文件...")
        
        # 准备上传数据
        files = {
            'file': ('测试健康指南.pdf', pdf_content, 'application/pdf')
        }
        data = {
            'character_id': 'xiyang',
            'user_id': 'test_user'
        }
        
        # 发送上传请求
        response = requests.post(
            'http://localhost:8001/upload-document',
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 上传成功: {result['message']}")
            print(f"📄 文件名: {result['filename']}")
            return True
        else:
            print(f"❌ 上传失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_document_list():
    """测试获取文档列表"""
    try:
        print("📋 获取文档列表...")
        response = requests.get('http://localhost:8001/documents/xiyang')
        
        if response.status_code == 200:
            result = response.json()
            print(f"📚 找到 {result['total']} 个文档:")
            for doc in result['files']:
                print(f"   - {doc['filename']} ({doc['file_size']} bytes)")
                if doc['summary']:
                    print(f"     摘要: {doc['summary'][:100]}...")
            return True
        else:
            print(f"❌ 获取文档列表失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 获取文档列表失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始PDF上传测试")
    
    # 测试上传
    result1 = asyncio.run(test_pdf_upload())
    
    if result1:
        # 测试文档列表
        result2 = asyncio.run(test_document_list())
        
        if result2:
            print("\n🎉 所有测试通过！PDF上传功能正常。")
        else:
            print("\n⚠️ 文档列表测试失败。")
    else:
        print("\n❌ PDF上传测试失败。")
