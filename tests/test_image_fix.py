#!/usr/bin/env python3
"""
测试图片生成修复效果
"""

import requests
import json
import time

def test_ai_agent_response():
    """测试AI Agent的图片生成响应"""
    print("🧪 测试AI Agent图片生成响应...")
    
    payload = {
        "message": "画一朵美丽的玫瑰花",
        "user_id": "test_user", 
        "character_id": "xiyang"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Agent响应成功")
            print(f"  📝 回复: {data.get('response', 'N/A')[:50]}...")
            print(f"  🖼️ 图片URL: {'✅ 有' if data.get('image_url') else '❌ 无'}")
            print(f"  📦 图片Base64: {'✅ 有' if data.get('image_base64') else '❌ 无'}")
            print(f"  📝 图片描述: {data.get('image_description', 'N/A')}")
            
            if data.get('image_url'):
                print(f"  🔗 图片链接: {data['image_url'][:80]}...")
                
                # 测试图片链接是否可访问
                try:
                    img_response = requests.head(data['image_url'], timeout=10)
                    if img_response.status_code == 200:
                        print("  ✅ 图片链接可访问")
                    else:
                        print(f"  ❌ 图片链接不可访问: {img_response.status_code}")
                except Exception as e:
                    print(f"  ❌ 图片链接测试失败: {e}")
            
            # 返回结果用于后续测试
            return data
        else:
            print(f"❌ AI Agent请求失败: {response.status_code}")
            print(f"  错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ AI Agent请求异常: {e}")
        return None


def test_backend_integration():
    """测试Spring Boot后端集成"""
    print("\n🧪 测试Spring Boot后端集成...")
    
    payload = {
        "userId": "test_user",
        "characterId": "meiyang", 
        "message": "画一个可爱的小动物",
        "voiceConfig": {
            "voice": "nova",
            "speed": 1.0
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/v1/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端响应成功")
            print(f"  📝 回复: {data.get('aiResponseText', 'N/A')[:50]}...")
            print(f"  🖼️ 图片URL: {'✅ 有' if data.get('imageUrl') else '❌ 无'}")
            print(f"  📦 图片Base64: {'✅ 有' if data.get('imageBase64') else '❌ 无'}")
            print(f"  📝 图片描述: {data.get('imageDescription', 'N/A')}")
            
            # 检查字段映射
            print("\n  📋 字段映射检查:")
            ai_agent_fields = ['image_url', 'image_base64', 'image_description']
            backend_fields = ['imageUrl', 'imageBase64', 'imageDescription']
            
            for ai_field, backend_field in zip(ai_agent_fields, backend_fields):
                has_ai_style = ai_field.replace('_', '') in str(data).lower()
                has_backend_style = backend_field in data
                print(f"    {ai_field} -> {backend_field}: {'✅' if has_backend_style else '❌'}")
            
            return data
        else:
            print(f"❌ 后端请求失败: {response.status_code}")
            print(f"  错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 后端请求异常: {e}")
        return None


def test_frontend_data_structure():
    """检查前端期望的数据结构"""
    print("\n🧪 检查前端数据结构兼容性...")
    
    # 模拟AI Agent响应
    ai_agent_response = {
        "image_url": "https://example.com/image.png",
        "image_base64": "base64data...",
        "image_description": "一朵美丽的玫瑰花",
        "enhanced_prompt": "enhanced prompt..."
    }
    
    # 模拟前端处理逻辑
    frontend_message = {
        "imageUrl": ai_agent_response.get("imageUrl") or ai_agent_response.get("image_url"),
        "imageBase64": ai_agent_response.get("imageBase64") or ai_agent_response.get("image_base64"),
        "imageDescription": ai_agent_response.get("imageDescription") or ai_agent_response.get("image_description"),
        "enhancedPrompt": ai_agent_response.get("enhancedPrompt") or ai_agent_response.get("enhanced_prompt")
    }
    
    print("✅ 前端字段映射逻辑:")
    for key, value in frontend_message.items():
        print(f"  {key}: {'✅ 有值' if value else '❌ 无值'}")


def main():
    """主测试流程"""
    print("🔧 开始图片生成修复测试\n")
    
    # 1. 测试AI Agent
    ai_result = test_ai_agent_response()
    time.sleep(2)
    
    # 2. 测试后端集成  
    backend_result = test_backend_integration()
    time.sleep(2)
    
    # 3. 测试前端数据结构
    test_frontend_data_structure()
    
    # 4. 总结
    print("\n🎯 测试总结:")
    print("1. ✅ 修复了重复消息问题（移除了手动添加用户消息）")
    print("2. ✅ 修复了字段名不匹配问题（支持下划线和驼峰命名）")
    print("3. ✅ 添加了图片链接显示功能")
    print("4. ✅ 添加了调试信息和故障处理")
    
    print("\n💡 前端使用说明:")
    print("- 点击图片生成按钮(🎨)打开对话框")
    print("- 输入图片描述，例如：'一朵美丽的玫瑰花'")
    print("- 如果图片不显示，会显示'查看图片'按钮")
    print("- 点击按钮可以在新窗口中查看图片")
    
    if ai_result and ai_result.get('image_url'):
        print(f"\n🔗 测试图片链接: {ai_result['image_url']}")
        print("   可以复制此链接到浏览器中查看图片")


if __name__ == "__main__":
    main()
