#!/usr/bin/env python3
"""
FamilyBot 集成测试脚本
测试整个系统的端到端功能
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any, List

class FamilyBotIntegrationTest:
    """FamilyBot集成测试类"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8080/api/v1"
        self.ai_agent_url = "http://localhost:8001"
        self.test_user_id = "test_user_" + str(int(time.time()))
        self.test_results: List[Dict[str, Any]] = []
    
    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
        if details and not success:
            print(f"   详情: {details}")
    
    def test_health_checks(self):
        """测试服务健康检查"""
        print("\n🏥 测试服务健康检查...")
        
        # 测试后端健康检查
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("后端健康检查", True, "后端服务正常")
            else:
                self.log_test("后端健康检查", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("后端健康检查", False, "连接失败", str(e))
        
        # 测试AI Agent健康检查
        try:
            response = requests.get(f"{self.ai_agent_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("AI Agent健康检查", True, "AI Agent服务正常")
            else:
                self.log_test("AI Agent健康检查", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("AI Agent健康检查", False, "连接失败", str(e))
    
    def test_character_management(self):
        """测试角色管理"""
        print("\n👥 测试角色管理...")
        
        # 测试获取角色列表
        try:
            response = requests.get(f"{self.backend_url}/characters", timeout=10)
            if response.status_code == 200:
                characters = response.json()
                if isinstance(characters, list) and len(characters) > 0:
                    self.log_test("获取角色列表", True, f"成功获取 {len(characters)} 个角色")
                    
                    # 测试角色切换
                    character_id = characters[0].get("characterId", "xiyang")
                    self.test_character_switch(character_id)
                else:
                    self.log_test("获取角色列表", False, "角色列表为空")
            else:
                self.log_test("获取角色列表", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("获取角色列表", False, "请求失败", str(e))
    
    def test_character_switch(self, character_id: str):
        """测试角色切换"""
        try:
            url = f"{self.backend_url}/characters/{character_id}/switch"
            params = {"userId": self.test_user_id}
            response = requests.post(url, params=params, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test("角色切换", True, f"成功切换到 {character_id}")
                else:
                    self.log_test("角色切换", False, result.get("message", "未知错误"))
            else:
                self.log_test("角色切换", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("角色切换", False, "请求失败", str(e))
    
    def test_chat_functionality(self):
        """测试聊天功能"""
        print("\n💬 测试聊天功能...")
        
        test_messages = [
            "你好！",
            "我想和你聊聊天",
            "你是谁？",
            "今天天气怎么样？",
            "我有点孤单"
        ]
        
        for message in test_messages:
            self.test_single_chat(message)
            time.sleep(1)  # 避免请求过快
    
    def test_single_chat(self, message: str):
        """测试单次聊天"""
        try:
            chat_data = {
                "message": message,
                "userId": self.test_user_id,
                "characterId": "xiyang"
            }
            
            response = requests.post(
                f"{self.backend_url}/chat", 
                json=chat_data, 
                timeout=30  # 增加超时时间，因为AI处理需要时间
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("response"):
                    self.log_test(
                        f"聊天测试", 
                        True, 
                        f"消息: '{message}' -> 回复: '{result['response'][:50]}...'"
                    )
                else:
                    self.log_test("聊天测试", False, "响应为空", result)
            else:
                self.log_test("聊天测试", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("聊天测试", False, f"消息'{message}'失败", str(e))
    
    def test_ai_agent_direct(self):
        """直接测试AI Agent"""
        print("\n🤖 直接测试AI Agent...")
        
        # 测试AI Agent的聊天接口
        try:
            chat_data = {
                "message": "你好，测试消息",
                "user_id": self.test_user_id,
                "character_id": "xiyang"
            }
            
            response = requests.post(
                f"{self.ai_agent_url}/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("response"):
                    self.log_test("AI Agent直接测试", True, "AI Agent响应正常")
                else:
                    self.log_test("AI Agent直接测试", False, "AI Agent响应为空", result)
            else:
                self.log_test("AI Agent直接测试", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("AI Agent直接测试", False, "请求失败", str(e))
    
    def test_conversation_history(self):
        """测试对话历史"""
        print("\n📚 测试对话历史...")
        
        try:
            params = {
                "userId": self.test_user_id,
                "characterId": "xiyang",
                "page": 0,
                "size": 10
            }
            
            response = requests.get(
                f"{self.backend_url}/conversations",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                conversation_count = result.get("totalElements", 0)
                self.log_test("对话历史", True, f"成功获取历史记录，共 {conversation_count} 条")
            else:
                self.log_test("对话历史", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("对话历史", False, "请求失败", str(e))
    
    def test_user_stats(self):
        """测试用户统计"""
        print("\n📊 测试用户统计...")
        
        try:
            response = requests.get(
                f"{self.backend_url}/users/{self.test_user_id}/stats",
                timeout=10
            )
            
            if response.status_code == 200:
                stats = response.json()
                total_conversations = stats.get("totalConversations", 0)
                self.log_test("用户统计", True, f"用户统计信息正常，对话数: {total_conversations}")
            else:
                self.log_test("用户统计", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("用户统计", False, "请求失败", str(e))
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*50)
        print("📋 FamilyBot 集成测试报告")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过: {passed_tests}")
        print(f"   失败: {failed_tests}")
        print(f"   成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"   - {test['test_name']}: {test['message']}")
        
        print(f"\n💾 测试用户ID: {self.test_user_id}")
        
        # 保存详细报告
        report_file = f"test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细报告已保存到: {report_file}")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始 FamilyBot 集成测试")
        print("测试用户ID:", self.test_user_id)
        
        # 运行各项测试
        self.test_health_checks()
        self.test_character_management()
        self.test_ai_agent_direct()
        self.test_chat_functionality()
        self.test_conversation_history()
        self.test_user_stats()
        
        # 生成报告
        all_passed = self.generate_report()
        
        if all_passed:
            print("\n🎉 所有测试通过！FamilyBot 系统运行正常！")
            return True
        else:
            print("\n⚠️  部分测试失败，请检查系统配置和服务状态")
            return False

def main():
    """主函数"""
    tester = FamilyBotIntegrationTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
