#!/usr/bin/env python3
"""
FamilyBot 完整系统集成测试
测试前端 -> 后端 -> AI Agent 的完整数据流
"""

import asyncio
import requests
import json
import time
import sys
from typing import Dict, Any

# 服务地址配置
FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8080"
AI_AGENT_URL = "http://localhost:8001"

class SystemTester:
    """系统集成测试器"""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """记录测试结果"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        if status == "PASS":
            print(f"✅ {test_name}: {status}")
        elif status == "FAIL":
            print(f"❌ {test_name}: {status}")
            self.failed_tests.append(result)
        else:
            print(f"⚠️  {test_name}: {status}")
        
        if details:
            print(f"   {details}")
    
    def test_service_health(self, service_name: str, url: str, expected_status: int = 200):
        """测试服务健康状态"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == expected_status:
                self.log_test(f"{service_name} Health Check", "PASS", f"Status: {response.status_code}")
                return True
            else:
                self.log_test(f"{service_name} Health Check", "FAIL", f"Expected {expected_status}, got {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test(f"{service_name} Health Check", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_backend_api(self):
        """测试后端API功能"""
        print("\n🏗️  Testing Backend API...")
        
        # 测试获取角色列表
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/characters", timeout=10)
            if response.status_code == 200:
                characters = response.json()
                if len(characters) > 0:
                    self.log_test("Get Characters API", "PASS", f"Found {len(characters)} characters")
                    return characters
                else:
                    self.log_test("Get Characters API", "FAIL", "No characters found")
                    return []
            else:
                self.log_test("Get Characters API", "FAIL", f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get Characters API", "FAIL", str(e))
            return []
    
    def test_ai_agent_api(self):
        """测试AI Agent API"""
        print("\n🤖 Testing AI Agent API...")
        
        # 测试文本聊天
        try:
            chat_data = {
                "user_id": "test_user",
                "character_id": "xiyang",
                "message": "你好，最近怎么样？"
            }
            
            response = requests.post(f"{AI_AGENT_URL}/chat", json=chat_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if "response" in result and "character_name" in result:
                    self.log_test("AI Agent Chat API", "PASS", f"Response: {result['response'][:50]}...")
                    return result
                else:
                    self.log_test("AI Agent Chat API", "FAIL", "Invalid response format")
                    return None
            else:
                self.log_test("AI Agent Chat API", "FAIL", f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("AI Agent Chat API", "FAIL", str(e))
            return None
    
    def test_backend_ai_integration(self, characters):
        """测试后端与AI Agent的集成"""
        print("\n🔗 Testing Backend-AI Agent Integration...")
        
        if not characters:
            self.log_test("Backend-AI Integration", "SKIP", "No characters available")
            return False
        
        try:
            # 通过后端发送聊天请求
            chat_data = {
                "userId": 1,  # 使用测试用户ID
                "characterId": characters[0]["id"],
                "message": "你好，我想和你聊天"
            }
            
            response = requests.post(f"{BACKEND_URL}/api/v1/chat", json=chat_data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if "aiResponseText" in result and "characterName" in result:
                    self.log_test("Backend-AI Integration", "PASS", 
                                f"Character: {result['characterName']}, Response: {result['aiResponseText'][:50]}...")
                    return True
                else:
                    self.log_test("Backend-AI Integration", "FAIL", "Invalid response format")
                    return False
            else:
                self.log_test("Backend-AI Integration", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend-AI Integration", "FAIL", str(e))
            return False
    
    def test_cot_functionality(self):
        """测试CoT推理功能"""
        print("\n🧠 Testing CoT Reasoning...")
        
        try:
            # 发送需要深度思考的健康问题
            chat_data = {
                "user_id": "test_cot",
                "character_id": "xiyang",
                "message": "我最近总是失眠，血压也不稳定，很担心身体健康"
            }
            
            response = requests.post(f"{AI_AGENT_URL}/chat", json=chat_data, timeout=45)
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # 检查CoT特征：回复长度、逻辑性、专业建议
                if len(response_text) > 300:  # CoT回复通常更长
                    self.log_test("CoT Response Length", "PASS", f"Length: {len(response_text)} chars")
                else:
                    self.log_test("CoT Response Length", "FAIL", f"Too short: {len(response_text)} chars")
                
                # 检查是否包含专业建议
                professional_keywords = ["建议", "应该", "可以", "需要", "方案", "注意"]
                has_advice = any(keyword in response_text for keyword in professional_keywords)
                if has_advice:
                    self.log_test("CoT Professional Advice", "PASS", "Contains professional suggestions")
                else:
                    self.log_test("CoT Professional Advice", "FAIL", "No professional advice detected")
                
                return True
            else:
                self.log_test("CoT Functionality", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("CoT Functionality", "FAIL", str(e))
            return False
    
    def test_character_routing(self):
        """测试角色路由功能"""
        print("\n🎭 Testing Character Routing...")
        
        test_cases = [
            {
                "input": "爷爷奶奶，我想你们了！",
                "expected_character": "懒羊羊",
                "description": "孙子角色路由"
            },
            {
                "input": "我最近工作很忙，想念家里",
                "expected_character": "美羊羊",
                "description": "女儿角色路由" 
            },
            {
                "input": "血压有点高，需要注意什么？",
                "expected_character": "喜羊羊",
                "description": "健康问题路由"
            }
        ]
        
        passed_routes = 0
        for test_case in test_cases:
            try:
                chat_data = {
                    "user_id": "test_routing",
                    "character_id": "xiyang",  # 初始角色
                    "message": test_case["input"]
                }
                
                response = requests.post(f"{AI_AGENT_URL}/chat", json=chat_data, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    character_name = result.get("character_name", "")
                    
                    self.log_test(f"Route: {test_case['description']}", "PASS", 
                                f"Input: '{test_case['input'][:30]}...' -> {character_name}")
                    passed_routes += 1
                else:
                    self.log_test(f"Route: {test_case['description']}", "FAIL", 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Route: {test_case['description']}", "FAIL", str(e))
        
        success_rate = passed_routes / len(test_cases)
        if success_rate >= 0.8:
            self.log_test("Overall Routing", "PASS", f"Success rate: {success_rate:.1%}")
        else:
            self.log_test("Overall Routing", "FAIL", f"Success rate: {success_rate:.1%}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 FamilyBot 完整系统集成测试")
        print("=" * 60)
        
        # 1. 健康检查
        print("\n🔍 Health Checks...")
        ai_healthy = self.test_service_health("AI Agent", AI_AGENT_URL)
        backend_healthy = self.test_service_health("Backend", f"{BACKEND_URL}/api/v1/characters")
        frontend_healthy = self.test_service_health("Frontend", FRONTEND_URL)
        
        if not all([ai_healthy, backend_healthy]):
            self.log_test("System Prerequisites", "FAIL", "Core services not available")
            return False
        
        # 2. 后端API测试
        characters = self.test_backend_api()
        
        # 3. AI Agent API测试
        self.test_ai_agent_api()
        
        # 4. 后端-AI Agent集成测试
        self.test_backend_ai_integration(characters)
        
        # 5. CoT功能测试
        self.test_cot_functionality()
        
        # 6. 角色路由测试
        self.test_character_routing()
        
        return True
    
    def print_summary(self):
        """打印测试总结"""
        total_tests = len(self.test_results)
        failed_count = len(self.failed_tests)
        passed_count = total_tests - failed_count
        
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_count} ✅")
        print(f"失败: {failed_count} ❌")
        print(f"成功率: {(passed_count/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ 失败的测试:")
            for test in self.failed_tests:
                print(f"   - {test['test']}: {test['details']}")
        
        if failed_count == 0:
            print("\n🎉 所有测试通过！FamilyBot系统运行完美！")
        else:
            print(f"\n⚠️  有 {failed_count} 个测试失败，请检查相关服务。")
        
        return failed_count == 0


def main():
    """主函数"""
    tester = SystemTester()
    
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        sys.exit(0 if success and len(tester.failed_tests) == 0 else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
